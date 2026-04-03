/**
 * TradeNetworkPanel - Manage trade network connections and recommendations
 * Refactored to use modular sub-components
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  UsersThree, 
  UserPlus, 
  Handshake,
  Sparkle,
  Lightning,
  ArrowRight
} from '@phosphor-icons/react';

import { RecommendedTraderCard, ConnectionCard, IncomingRequestCard, OutgoingRequestCard } from './network';

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
        <div className="text-[var(--text-muted)]">Loading your trade network...</div>
      </div>
    );
  }

  const incomingCount = pendingRequests.incoming?.length || 0;

  return (
    <div className="max-w-3xl mx-auto" data-testid="trade-network-panel">
      <div className="flex items-center gap-2 mb-4 md:mb-6">
        <Handshake size={24} weight="duotone" className="text-[var(--brand-primary)]" />
        <h2 className="text-xl md:text-2xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          My Trade Network
        </h2>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 md:gap-2 mb-4 md:mb-6 border-b border-[var(--bg-surface-hover)] overflow-x-auto">
        <button
          onClick={() => setActiveTab('recommended')}
          className={`px-3 md:px-4 py-2.5 text-sm font-medium transition-all border-b-2 -mb-px flex items-center gap-1.5 whitespace-nowrap ${
            activeTab === 'recommended'
              ? 'text-[#F59E0B] border-[#F59E0B]'
              : 'text-[var(--text-muted)] border-transparent hover:text-[var(--text-secondary)]'
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
              ? 'text-[var(--brand-primary)] border-[var(--brand-primary)]'
              : 'text-[var(--text-muted)] border-transparent hover:text-[var(--text-secondary)]'
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
              ? 'text-[var(--brand-primary)] border-[var(--brand-primary)]'
              : 'text-[var(--text-muted)] border-transparent hover:text-[var(--text-secondary)]'
          }`}
          data-testid="tab-requests"
        >
          <UserPlus size={18} weight={activeTab === 'requests' ? 'fill' : 'regular'} />
          Requests
          {incomingCount > 0 && (
            <span className="bg-[var(--brand-primary)] text-white text-xs px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
              {incomingCount}
            </span>
          )}
        </button>
      </div>

      {/* Recommended Tab */}
      {activeTab === 'recommended' && (
        <div className="space-y-3" data-testid="recommended-list">
          {recommendations.length === 0 ? (
            <div className="theme-surface border theme-border p-6 md:p-8 text-center">
              <Sparkle size={48} className="mx-auto theme-text-muted mb-4" />
              <h3 className="text-lg font-semibold theme-text-primary mb-2">No recommendations yet</h3>
              <p className="text-sm theme-text-muted">
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
                <RecommendedTraderCard
                  key={rec.id}
                  recommendation={rec}
                  onConnect={handleSendRequest}
                  onViewProfile={onViewProfile}
                  isLoading={actionLoading === rec.id}
                />
              ))}
            </>
          )}
        </div>
      )}

      {/* Connections Tab */}
      {activeTab === 'connections' && (
        <div className="space-y-3" data-testid="connections-list">
          {connections.length === 0 ? (
            <div className="theme-surface border theme-border p-6 md:p-8 text-center">
              <UsersThree size={48} className="mx-auto theme-text-muted mb-4" />
              <h3 className="text-lg font-semibold theme-text-primary mb-2">No connections yet</h3>
              <p className="text-sm theme-text-muted">
                Start building your trade network by sending requests to other traders
              </p>
            </div>
          ) : (
            connections.map((connection) => (
              <ConnectionCard
                key={connection.id}
                connection={connection}
                onRemove={handleRemoveConnection}
                onViewProfile={onViewProfile}
                isLoading={actionLoading === connection.id}
              />
            ))
          )}
        </div>
      )}

      {/* Requests Tab */}
      {activeTab === 'requests' && (
        <div className="space-y-6" data-testid="requests-section">
          {/* Incoming Requests */}
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3 flex items-center gap-2">
              <ArrowRight size={14} className="rotate-180" />
              Incoming Requests ({pendingRequests.incoming?.length || 0})
            </h3>
            {pendingRequests.incoming?.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)] italic">No pending requests</p>
            ) : (
              <div className="space-y-3">
                {pendingRequests.incoming.map((request) => (
                  <IncomingRequestCard
                    key={request.id}
                    request={request}
                    onAccept={handleAcceptRequest}
                    onDecline={handleDeclineRequest}
                    isLoading={actionLoading === request.id}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Outgoing Requests */}
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3 flex items-center gap-2">
              <ArrowRight size={14} />
              Sent Requests ({pendingRequests.outgoing?.length || 0})
            </h3>
            {pendingRequests.outgoing?.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)] italic">No pending requests</p>
            ) : (
              <div className="space-y-3">
                {pendingRequests.outgoing.map((request) => (
                  <OutgoingRequestCard
                    key={request.id}
                    request={request}
                    onCancel={handleCancelRequest}
                    isLoading={actionLoading === request.id}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
