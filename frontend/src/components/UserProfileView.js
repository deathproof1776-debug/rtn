import { useState, useEffect, useCallback } from 'react';
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
  Handshake,
  CaretDown,
  CaretUp,
  Images
} from '@phosphor-icons/react';

// Expandable Bio component for long descriptions
function ExpandableBio({ bio, charLimit = 150 }) {
  const [expanded, setExpanded] = useState(false);
  
  if (!bio) return null;
  
  const needsTruncation = bio.length > charLimit;
  const displayText = expanded || !needsTruncation ? bio : bio.slice(0, charLimit) + '...';
  
  return (
    <div>
      <p className="text-sm text-[#A8A29E]">{displayText}</p>
      {needsTruncation && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1 text-xs text-[#B45309] hover:text-[#D97706] mt-1 transition-colors"
          data-testid="expand-bio"
        >
          {expanded ? (
            <>Show less <CaretUp size={12} /></>
          ) : (
            <>Read more <CaretDown size={12} /></>
          )}
        </button>
      )}
    </div>
  );
}

// Helper to normalize items (handle both string and object formats)
const getItemDisplay = (item) => {
  if (typeof item === 'string') {
    return { name: item, description: '', quantity: '' };
  }
  return { name: item.name || '', description: item.description || '', quantity: item.quantity || '' };
};

// Expandable section component for profile items with detailed display and scrolling
function ExpandableSection({ title, items, badgeClass, icon: Icon, iconColor, initialLimit = 4, maxHeight = 120 }) {
  const [expanded, setExpanded] = useState(false);
  const [showItemDetails, setShowItemDetails] = useState(null);
  
  if (!items || items.length === 0) return null;
  
  const hasMore = items.length > initialLimit;
  
  return (
    <div className="bg-[#0C0A09] p-3 border border-[#292524]">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs uppercase tracking-wider font-semibold" style={{ color: iconColor }}>
          {title} <span className="text-[#78716C] font-normal">({items.length})</span>
        </div>
        {hasMore && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-[#78716C] hover:text-[#B45309] transition-colors"
            data-testid={`expand-${title.toLowerCase().replace(/\s+/g, '-')}`}
          >
            {expanded ? (
              <>Collapse <CaretUp size={12} /></>
            ) : (
              <>Expand <CaretDown size={12} /></>
            )}
          </button>
        )}
      </div>
      <div 
        className={`flex flex-wrap gap-1 overflow-y-auto scrollbar-thin pr-1 ${expanded ? '' : ''}`}
        style={{ maxHeight: expanded ? '200px' : `${maxHeight}px` }}
      >
        {items.map((item, i) => {
          const itemData = getItemDisplay(item);
          const hasDetails = itemData.description || itemData.quantity;
          const isShowingDetails = showItemDetails === i;
          
          return (
            <div key={`${title}-${itemData.name}-${i}`} className="relative">
              <button
                onClick={() => hasDetails && setShowItemDetails(isShowingDetails ? null : i)}
                className={`badge ${badgeClass} text-[10px] ${hasDetails ? 'cursor-pointer hover:opacity-80' : ''}`}
                title={hasDetails ? 'Click for details' : ''}
              >
                {itemData.name}
                {itemData.quantity && <span className="ml-1 opacity-75">({itemData.quantity})</span>}
                {hasDetails && !itemData.quantity && <span className="ml-1 opacity-50">•</span>}
              </button>
              
              {/* Details tooltip */}
              {isShowingDetails && hasDetails && (
                <div className="absolute z-50 left-0 top-full mt-1 bg-[#1C1917] border border-[#44403C] p-2 min-w-[180px] max-w-[250px] text-[10px] shadow-lg">
                  {itemData.quantity && (
                    <div className="text-[#A8A29E] mb-1">
                      <span className="text-[#78716C]">Qty:</span> {itemData.quantity}
                    </div>
                  )}
                  {itemData.description && (
                    <div className="text-[#A8A29E]">
                      <span className="text-[#78716C]">Details:</span> {itemData.description}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Click outside to close details tooltip */}
      {showItemDetails !== null && (
        <div className="fixed inset-0 z-40" onClick={() => setShowItemDetails(null)} />
      )}
    </div>
  );
}

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function UserProfileView({ userId, onClose, onStartChat, onProposeTrade, onViewGallery }) {
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [networkStatus, setNetworkStatus] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [galleryCount, setGalleryCount] = useState(0);

  const fetchProfile = useCallback(async () => {
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
  }, [userId]);

  const fetchNetworkStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/network/status/${userId}`, {
        withCredentials: true
      });
      setNetworkStatus(response.data);
    } catch (error) {
      console.error('Error fetching network status:', error);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) {
      fetchProfile();
      fetchNetworkStatus();
      // Fetch gallery count
      axios.get(`${API_URL}/api/gallery/${userId}`, { withCredentials: true })
        .then(res => setGalleryCount(res.data.total || 0))
        .catch(() => setGalleryCount(0));
    }
  }, [userId, fetchProfile, fetchNetworkStatus]);

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
              <button
                onClick={() => {
                  if (onProposeTrade) {
                    onClose();
                    onProposeTrade(userId, profile?.name || 'Unknown');
                  }
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-[#44403C] text-[#A8A29E] text-sm hover:border-[#B45309] hover:text-[#B45309]"
                data-testid="propose-trade-user-btn"
              >
                <ArrowsLeftRight size={16} />
                Propose Trade
              </button>
              {galleryCount > 0 && (
                <button
                  onClick={() => {
                    if (onViewGallery) {
                      onClose();
                      onViewGallery(userId, profile?.name || 'Unknown');
                    }
                  }}
                  className="flex items-center gap-1.5 px-3 py-1.5 border border-[#44403C] text-[#A8A29E] text-sm hover:border-[#B45309] hover:text-[#B45309]"
                  data-testid="view-gallery-btn"
                >
                  <Images size={16} />
                  Gallery ({galleryCount})
                </button>
              )}
            </div>
          )}

          {/* Bio */}
          {profile.bio && (
            <ExpandableBio bio={profile.bio} charLimit={150} />
          )}

          {/* Skills */}
          {profile.skills?.length > 0 && (
            <ExpandableSection
              title="Skills"
              items={profile.skills}
              badgeClass="tag"
              icon={Tag}
              iconColor="#B45309"
              initialLimit={6}
            />
          )}

          {/* Offerings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ExpandableSection
              title="Goods Offering"
              items={profile.goods_offering}
              badgeClass="badge-offering"
              iconColor="#4D7C0F"
              initialLimit={5}
            />

            <ExpandableSection
              title="Goods Wanted"
              items={profile.goods_wanted}
              badgeClass="badge-looking"
              iconColor="#B45309"
              initialLimit={5}
            />

            <ExpandableSection
              title="Services Offering"
              items={profile.services_offering}
              badgeClass="badge-offering"
              iconColor="#4D7C0F"
              initialLimit={5}
            />

            <ExpandableSection
              title="Services Wanted"
              items={profile.services_wanted}
              badgeClass="badge-looking"
              iconColor="#B45309"
              initialLimit={5}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
