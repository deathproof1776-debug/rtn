import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  UsersThree, 
  UserPlus, 
  Check, 
  X, 
  MapPin,
  SealCheck,
  UserMinus,
  Clock,
  ArrowRight,
  Handshake,
  Sparkle,
  Lightning
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function TradeNetworkPanel({ onViewProfile }) {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('connections');
  const [connections, setConnections] = useState([]);
  const [pendingRequests, setPendingRequests] = useState({ incoming: [], outgoing: [] });
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [connectionsRes, requestsRes, recommendedRes] = await Promise.all([
        axios.get(`${API_URL}/api/network/connections`, { withCredentials: true }),
        axios.get(`${API_URL}/api/network/requests/pending`, { withCredentials: true }),
        axios.get(`${API_URL}/api/network/recommended`, { withCredentials: true })
      ]);
      setConnections(connectionsRes.data.connections || []);
      setPendingRequests(requestsRes.data || { incoming: [], outgoing: [] });
      setRecommendations(recommendedRes.data.recommendations || []);
    } catch (error) {
      console.error('Error fetching network data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRequest = async (requestId) => {
    setActionLoading(requestId);
    try {
      await axios.post(`${API_URL}/api/network/respond`, {
        request_id: requestId,
        accept: true
      }, { withCredentials: true });
      await fetchData();
    } catch (error) {
      console.error('Error accepting request:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeclineRequest = async (requestId) => {
    setActionLoading(requestId);
    try {
      await axios.post(`${API_URL}/api/network/respond`, {
        request_id: requestId,
        accept: false
      }, { withCredentials: true });
      await fetchData();
    } catch (error) {
      console.error('Error declining request:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancelRequest = async (requestId) => {
    setActionLoading(requestId);
    try {
      await axios.post(`${API_URL}/api/network/cancel/${requestId}`, {}, { withCredentials: true });
      await fetchData();
    } catch (error) {
      console.error('Error cancelling request:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRemoveConnection = async (userId) => {
    setActionLoading(userId);
    try {
      await axios.delete(`${API_URL}/api/network/connections/${userId}`, { withCredentials: true });
      await fetchData();
    } catch (error) {
      console.error('Error removing connection:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleSendRequest = async (userId) => {
    setActionLoading(userId);
    try {
      await axios.post(`${API_URL}/api/network/request`, {
        target_user_id: userId
      }, { withCredentials: true });
      await fetchData();
    } catch (error) {
      console.error('Error sending request:', error);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-[#78716C]">Loading your trade network...</div>
      </div>
    );
  }

  const incomingCount = pendingRequests.incoming?.length || 0;

  return (
    <div className="max-w-3xl mx-auto" data-testid="trade-network-panel">
      <div className="flex items-center gap-2 mb-4 md:mb-6">
        <Handshake size={24} weight="duotone" className="text-[#B45309]" />
        <h2 className="text-xl md:text-2xl font-bold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          My Trade Network
        </h2>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 md:gap-2 mb-4 md:mb-6 border-b border-[#292524] overflow-x-auto">
        <button
          onClick={() => setActiveTab('recommended')}
          className={`px-3 md:px-4 py-2.5 text-sm font-medium transition-all border-b-2 -mb-px flex items-center gap-1.5 whitespace-nowrap ${
            activeTab === 'recommended'
              ? 'text-[#F59E0B] border-[#F59E0B]'
              : 'text-[#78716C] border-transparent hover:text-[#A8A29E]'
          }`}
          data-testid="tab-recommended"
        >
          <Sparkle size={18} weight={activeTab === 'recommended' ? 'fill' : 'regular'} />
          <span className="hidden sm:inline">Recommended</span>
          <span className="sm:hidden">Find</span>
          {recommendations.length > 0 && (
            <span className="bg-[#F59E0B]/20 text-[#F59E0B] text-xs px-1.5 py-0.5 rounded-full">
              {recommendations.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('connections')}
          className={`px-3 md:px-4 py-2.5 text-sm font-medium transition-all border-b-2 -mb-px whitespace-nowrap ${
            activeTab === 'connections'
              ? 'text-[#B45309] border-[#B45309]'
              : 'text-[#78716C] border-transparent hover:text-[#A8A29E]'
          }`}
          data-testid="tab-connections"
        >
          <UsersThree size={18} className="inline mr-1.5" weight={activeTab === 'connections' ? 'fill' : 'regular'} />
          Network ({connections.length})
        </button>
        <button
          onClick={() => setActiveTab('requests')}
          className={`px-3 md:px-4 py-2.5 text-sm font-medium transition-all border-b-2 -mb-px flex items-center gap-1.5 whitespace-nowrap ${
            activeTab === 'requests'
              ? 'text-[#B45309] border-[#B45309]'
              : 'text-[#78716C] border-transparent hover:text-[#A8A29E]'
          }`}
          data-testid="tab-requests"
        >
          <UserPlus size={18} weight={activeTab === 'requests' ? 'fill' : 'regular'} />
          Requests
          {incomingCount > 0 && (
            <span className="bg-[#B45309] text-white text-xs px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
              {incomingCount}
            </span>
          )}
        </button>
      </div>

      {/* Recommended Tab */}
      {activeTab === 'recommended' && (
        <div className="space-y-3" data-testid="recommended-list">
          {recommendations.length === 0 ? (
            <div className="bg-[#1C1917] border border-[#292524] p-6 md:p-8 text-center">
              <Sparkle size={48} className="mx-auto text-[#44403C] mb-4" />
              <h3 className="text-lg font-semibold text-[#E7E5E4] mb-2">No recommendations yet</h3>
              <p className="text-sm text-[#78716C]">
                Update your profile with goods and services you're offering and looking for to get personalized recommendations
              </p>
            </div>
          ) : (
            <>
              <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 p-3 mb-4">
                <div className="flex items-center gap-2 text-[#F59E0B]">
                  <Lightning size={18} weight="fill" />
                  <span className="text-sm font-medium">
                    {recommendations.length} traders match your interests
                  </span>
                </div>
              </div>
              {recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="bg-[#1C1917] border border-[#292524] border-l-2 border-l-[#F59E0B] p-4 hover:border-[#F59E0B]/50 transition-colors"
                  data-testid={`recommended-${rec.id}`}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-[#292524] flex items-center justify-center text-[#F59E0B] font-semibold text-lg flex-shrink-0">
                      {rec.avatar ? (
                        <img src={rec.avatar} alt="" className="w-full h-full object-cover" />
                      ) : (
                        rec.name?.charAt(0)?.toUpperCase() || 'U'
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span 
                          className="font-medium text-[#E7E5E4] truncate cursor-pointer hover:text-[#F59E0B]"
                          onClick={() => onViewProfile && onViewProfile(rec.id)}
                        >
                          {rec.name}
                        </span>
                        {rec.is_verified && (
                          <span className="verified-badge">
                            <SealCheck size={10} weight="fill" />
                            Verified
                          </span>
                        )}
                      </div>
                      {rec.location && (
                        <div className="flex items-center gap-1 text-xs text-[#78716C] mb-2">
                          <MapPin size={10} />
                          {rec.location}
                        </div>
                      )}
                      {/* Match reason */}
                      <div className="text-xs text-[#F59E0B] mb-2 font-medium">
                        {rec.reason}
                      </div>
                      {/* What they offer that you want */}
                      {rec.offers_you_want?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-1">
                          {rec.offers_you_want.map((item, i) => (
                            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-[#15803D]/20 text-[#22C55E] border border-[#15803D]/30">
                              Offers: {item}
                            </span>
                          ))}
                        </div>
                      )}
                      {/* What they want that you offer */}
                      {rec.wants_you_offer?.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {rec.wants_you_offer.map((item, i) => (
                            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-[#B45309]/20 text-[#F59E0B] border border-[#B45309]/30">
                              Wants: {item}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => handleSendRequest(rec.id)}
                      disabled={actionLoading === rec.id}
                      className="flex items-center gap-1.5 px-3 py-2 bg-[#F59E0B] text-black text-sm font-medium hover:bg-[#D97706] transition-colors disabled:opacity-50 flex-shrink-0"
                      data-testid={`add-recommended-${rec.id}`}
                    >
                      <UserPlus size={16} />
                      <span className="hidden sm:inline">Connect</span>
                    </button>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {/* Connections Tab */}
      {activeTab === 'connections' && (
        <div className="space-y-3" data-testid="connections-list">
          {connections.length === 0 ? (
            <div className="bg-[#1C1917] border border-[#292524] p-6 md:p-8 text-center">
              <UsersThree size={48} className="mx-auto text-[#44403C] mb-4" />
              <h3 className="text-lg font-semibold text-[#E7E5E4] mb-2">No connections yet</h3>
              <p className="text-sm text-[#78716C]">
                Start building your trade network by sending requests to other traders
              </p>
            </div>
          ) : (
            connections.map((connection) => (
              <div
                key={connection.id}
                className="bg-[#1C1917] border border-[#292524] p-4 flex items-center gap-4 hover:border-[#B45309]/30 transition-colors"
                data-testid={`connection-${connection.id}`}
              >
                <div className="w-12 h-12 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold text-lg flex-shrink-0">
                  {connection.avatar ? (
                    <img src={connection.avatar} alt="" className="w-full h-full object-cover" />
                  ) : (
                    connection.name?.charAt(0)?.toUpperCase() || 'U'
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span 
                      className="font-medium text-[#E7E5E4] truncate cursor-pointer hover:text-[#B45309]"
                      onClick={() => onViewProfile && onViewProfile(connection.id)}
                    >
                      {connection.name}
                    </span>
                    {connection.is_verified && (
                      <span className="verified-badge">
                        <SealCheck size={10} weight="fill" />
                        Verified Trader
                      </span>
                    )}
                  </div>
                  {connection.location && (
                    <div className="flex items-center gap-1 text-xs text-[#78716C] mt-0.5">
                      <MapPin size={10} />
                      {connection.location}
                    </div>
                  )}
                  {connection.skills?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {connection.skills.slice(0, 3).map((skill, i) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 bg-[#292524] text-[#A8A29E]">
                          {skill}
                        </span>
                      ))}
                      {connection.skills.length > 3 && (
                        <span className="text-[10px] text-[#78716C]">+{connection.skills.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleRemoveConnection(connection.id)}
                  disabled={actionLoading === connection.id}
                  className="p-2 text-[#991B1B] hover:bg-[#991B1B]/10 transition-colors disabled:opacity-50"
                  title="Remove from network"
                  data-testid={`remove-connection-${connection.id}`}
                >
                  <UserMinus size={20} />
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {/* Requests Tab */}
      {activeTab === 'requests' && (
        <div className="space-y-6" data-testid="requests-section">
          {/* Incoming Requests */}
          <div>
            <h3 className="text-sm font-semibold text-[#A8A29E] uppercase tracking-wider mb-3 flex items-center gap-2">
              <ArrowRight size={14} className="rotate-180" />
              Incoming Requests ({pendingRequests.incoming?.length || 0})
            </h3>
            {pendingRequests.incoming?.length === 0 ? (
              <p className="text-sm text-[#78716C] italic">No pending requests</p>
            ) : (
              <div className="space-y-3">
                {pendingRequests.incoming.map((request) => (
                  <div
                    key={request.id}
                    className="bg-[#1C1917] border border-[#B45309]/30 p-4 flex items-center gap-4"
                    data-testid={`incoming-request-${request.id}`}
                  >
                    <div className="w-10 h-10 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold flex-shrink-0">
                      {request.from_user_avatar ? (
                        <img src={request.from_user_avatar} alt="" className="w-full h-full object-cover" />
                      ) : (
                        request.from_user_name?.charAt(0)?.toUpperCase() || 'U'
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-[#E7E5E4]">{request.from_user_name}</span>
                        {request.is_verified && (
                          <span className="verified-badge">
                            <SealCheck size={10} weight="fill" />
                            Verified
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1 text-xs text-[#78716C]">
                        <Clock size={10} />
                        {formatDistanceToNow(new Date(request.created_at), { addSuffix: true })}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAcceptRequest(request.id)}
                        disabled={actionLoading === request.id}
                        className="p-2 bg-[#15803D]/20 text-[#22C55E] hover:bg-[#15803D]/30 transition-colors disabled:opacity-50"
                        title="Accept"
                        data-testid={`accept-request-${request.id}`}
                      >
                        <Check size={18} weight="bold" />
                      </button>
                      <button
                        onClick={() => handleDeclineRequest(request.id)}
                        disabled={actionLoading === request.id}
                        className="p-2 bg-[#991B1B]/20 text-[#EF4444] hover:bg-[#991B1B]/30 transition-colors disabled:opacity-50"
                        title="Decline"
                        data-testid={`decline-request-${request.id}`}
                      >
                        <X size={18} weight="bold" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Outgoing Requests */}
          <div>
            <h3 className="text-sm font-semibold text-[#A8A29E] uppercase tracking-wider mb-3 flex items-center gap-2">
              <ArrowRight size={14} />
              Sent Requests ({pendingRequests.outgoing?.length || 0})
            </h3>
            {pendingRequests.outgoing?.length === 0 ? (
              <p className="text-sm text-[#78716C] italic">No pending requests</p>
            ) : (
              <div className="space-y-3">
                {pendingRequests.outgoing.map((request) => (
                  <div
                    key={request.id}
                    className="bg-[#1C1917] border border-[#292524] p-4 flex items-center gap-4"
                    data-testid={`outgoing-request-${request.id}`}
                  >
                    <div className="w-10 h-10 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold flex-shrink-0">
                      {request.to_user_avatar ? (
                        <img src={request.to_user_avatar} alt="" className="w-full h-full object-cover" />
                      ) : (
                        request.to_user_name?.charAt(0)?.toUpperCase() || 'U'
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-[#E7E5E4]">{request.to_user_name}</span>
                        {request.is_verified && (
                          <span className="verified-badge">
                            <SealCheck size={10} weight="fill" />
                            Verified
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1 text-xs text-[#78716C]">
                        <Clock size={10} />
                        Sent {formatDistanceToNow(new Date(request.created_at), { addSuffix: true })}
                      </div>
                    </div>
                    <button
                      onClick={() => handleCancelRequest(request.id)}
                      disabled={actionLoading === request.id}
                      className="px-3 py-1.5 text-xs border border-[#44403C] text-[#A8A29E] hover:border-[#991B1B] hover:text-[#EF4444] transition-colors disabled:opacity-50"
                      data-testid={`cancel-request-${request.id}`}
                    >
                      Cancel
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
