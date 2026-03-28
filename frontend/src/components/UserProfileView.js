import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  User, 
  MapPin, 
  Tag, 
  ArrowsLeftRight,
  SealCheck,
  UserPlus,
  UsersThree,
  Clock,
  X,
  ChatCircle,
  Handshake
} from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function UserProfileView({ userId, onClose, onStartChat }) {
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [networkStatus, setNetworkStatus] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (userId) {
      fetchProfile();
      fetchNetworkStatus();
    }
  }, [userId]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/profile/${userId}`, {
        withCredentials: true
      });
      setProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNetworkStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/network/status/${userId}`, {
        withCredentials: true
      });
      setNetworkStatus(response.data);
    } catch (error) {
      console.error('Error fetching network status:', error);
    }
  };

  const handleSendRequest = async () => {
    setActionLoading(true);
    try {
      await axios.post(`${API_URL}/api/network/request`, {
        target_user_id: userId
      }, { withCredentials: true });
      await fetchNetworkStatus();
    } catch (error) {
      console.error('Error sending request:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancelRequest = async () => {
    if (!networkStatus?.request_id) return;
    setActionLoading(true);
    try {
      await axios.post(`${API_URL}/api/network/cancel/${networkStatus.request_id}`, {}, { withCredentials: true });
      await fetchNetworkStatus();
    } catch (error) {
      console.error('Error cancelling request:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAcceptRequest = async () => {
    if (!networkStatus?.request_id) return;
    setActionLoading(true);
    try {
      await axios.post(`${API_URL}/api/network/respond`, {
        request_id: networkStatus.request_id,
        accept: true
      }, { withCredentials: true });
      await fetchNetworkStatus();
    } catch (error) {
      console.error('Error accepting request:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRemoveConnection = async () => {
    setActionLoading(true);
    try {
      await axios.delete(`${API_URL}/api/network/connections/${userId}`, { withCredentials: true });
      await fetchNetworkStatus();
    } catch (error) {
      console.error('Error removing connection:', error);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
        <div className="bg-[#1C1917] border border-[#292524] p-8 max-w-lg w-full">
          <div className="text-[#78716C] text-center">Loading profile...</div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
        <div className="bg-[#1C1917] border border-[#292524] p-8 max-w-lg w-full text-center">
          <p className="text-[#A8A29E]">User not found</p>
          <button onClick={onClose} className="btn-secondary mt-4">Close</button>
        </div>
      </div>
    );
  }

  const isOwnProfile = currentUser?.id === userId;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" data-testid="user-profile-modal">
      <div className="bg-[#1C1917] border border-[#B45309] max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#292524]">
          <h2 className="text-lg font-bold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Trader Profile
          </h2>
          <button onClick={onClose} className="p-1.5 text-[#78716C] hover:text-[#E7E5E4]" data-testid="close-profile-modal">
            <X size={20} />
          </button>
        </div>

        {/* Profile Content */}
        <div className="p-4 md:p-6 space-y-5">
          {/* Avatar & Basic Info */}
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-[#292524] flex items-center justify-center text-[#B45309] text-2xl font-bold flex-shrink-0">
              {profile.avatar ? (
                <img src={profile.avatar} alt="" className="w-full h-full object-cover" />
              ) : (
                profile.name?.charAt(0)?.toUpperCase() || 'U'
              )}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-lg font-semibold text-[#E7E5E4]">{profile.name}</h3>
                {profile.is_verified && (
                  <span className="verified-badge verified-badge-lg" data-testid="profile-verified">
                    <SealCheck size={12} weight="fill" />
                    Verified Trader
                  </span>
                )}
              </div>
              {profile.location && (
                <div className="flex items-center gap-1 text-sm text-[#78716C] mt-1">
                  <MapPin size={14} />
                  {profile.location}
                </div>
              )}
            </div>
          </div>

          {/* Network Status & Action Buttons */}
          {!isOwnProfile && networkStatus && (
            <div className="flex flex-wrap gap-2">
              {networkStatus.status === 'connected' && (
                <>
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#15803D]/20 text-[#22C55E] text-sm">
                    <Handshake size={16} weight="fill" />
                    In Your Network
                  </div>
                  <button
                    onClick={handleRemoveConnection}
                    disabled={actionLoading}
                    className="px-3 py-1.5 border border-[#991B1B] text-[#EF4444] text-sm hover:bg-[#991B1B]/10 disabled:opacity-50"
                    data-testid="remove-from-network-btn"
                  >
                    Remove
                  </button>
                </>
              )}
              {networkStatus.status === 'pending_sent' && (
                <button
                  onClick={handleCancelRequest}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 border border-[#44403C] text-[#A8A29E] text-sm hover:border-[#B45309] disabled:opacity-50"
                  data-testid="cancel-request-btn"
                >
                  <Clock size={16} />
                  Request Pending - Cancel
                </button>
              )}
              {networkStatus.status === 'pending_received' && (
                <button
                  onClick={handleAcceptRequest}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-[#B45309] text-white text-sm hover:bg-[#92400E] disabled:opacity-50"
                  data-testid="accept-request-btn"
                >
                  <UserPlus size={16} />
                  Accept Network Request
                </button>
              )}
              {networkStatus.status === 'none' && (
                <button
                  onClick={handleSendRequest}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-[#B45309] text-white text-sm hover:bg-[#92400E] disabled:opacity-50"
                  data-testid="add-to-network-btn"
                >
                  <UserPlus size={16} />
                  Add to Trade Network
                </button>
              )}
              <button
                onClick={() => onStartChat && onStartChat(userId)}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-[#44403C] text-[#A8A29E] text-sm hover:border-[#B45309] hover:text-[#B45309]"
                data-testid="message-user-btn"
              >
                <ChatCircle size={16} />
                Message
              </button>
            </div>
          )}

          {/* Bio */}
          {profile.bio && (
            <div>
              <p className="text-sm text-[#A8A29E]">{profile.bio}</p>
            </div>
          )}

          {/* Skills */}
          {profile.skills?.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Tag size={14} className="text-[#B45309]" />
                <span className="text-xs uppercase tracking-wider text-[#78716C] font-semibold">Skills</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {profile.skills.map((skill, i) => (
                  <span key={i} className="tag text-xs">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {/* Offerings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Goods Offering */}
            {profile.goods_offering?.length > 0 && (
              <div className="bg-[#0C0A09] p-3 border border-[#292524]">
                <div className="text-xs uppercase tracking-wider text-[#4D7C0F] font-semibold mb-2">Goods Offering</div>
                <div className="flex flex-wrap gap-1">
                  {profile.goods_offering.map((item, i) => (
                    <span key={i} className="badge badge-offering text-[10px]">{item}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Goods Wanted */}
            {profile.goods_wanted?.length > 0 && (
              <div className="bg-[#0C0A09] p-3 border border-[#292524]">
                <div className="text-xs uppercase tracking-wider text-[#B45309] font-semibold mb-2">Goods Wanted</div>
                <div className="flex flex-wrap gap-1">
                  {profile.goods_wanted.map((item, i) => (
                    <span key={i} className="badge badge-looking text-[10px]">{item}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Services Offering */}
            {profile.services_offering?.length > 0 && (
              <div className="bg-[#0C0A09] p-3 border border-[#292524]">
                <div className="text-xs uppercase tracking-wider text-[#4D7C0F] font-semibold mb-2">Services Offering</div>
                <div className="flex flex-wrap gap-1">
                  {profile.services_offering.map((item, i) => (
                    <span key={i} className="badge badge-offering text-[10px]">{item}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Services Wanted */}
            {profile.services_wanted?.length > 0 && (
              <div className="bg-[#0C0A09] p-3 border border-[#292524]">
                <div className="text-xs uppercase tracking-wider text-[#B45309] font-semibold mb-2">Services Wanted</div>
                <div className="flex flex-wrap gap-1">
                  {profile.services_wanted.map((item, i) => (
                    <span key={i} className="badge badge-looking text-[10px]">{item}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
