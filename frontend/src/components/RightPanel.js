import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowsLeftRight, Lightning, Users, MapPin, NavigationArrow, SealCheck, Handshake } from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Helper to get display name from item (handles both string and object formats)
const getItemName = (item) => {
  if (typeof item === 'string') return item;
  return item?.name || '';
};

export default function RightPanel({ matches, onViewProfile }) {
  const [nearbyUsers, setNearbyUsers] = useState([]);
  const [userLocation, setUserLocation] = useState('');
  const [loadingNearby, setLoadingNearby] = useState(true);
  const [networkCount, setNetworkCount] = useState(0);

  useEffect(() => {
    fetchNearbyUsers();
    fetchNetworkCount();
  }, []);

  const fetchNearbyUsers = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/users/nearby`, {
        withCredentials: true
      });
      setNearbyUsers(res.data.nearby_users || []);
      setUserLocation(res.data.user_location || '');
    } catch (error) {
      console.error('Error fetching nearby users:', error);
    } finally {
      setLoadingNearby(false);
    }
  };

  const fetchNetworkCount = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/network/connections`, {
        withCredentials: true
      });
      setNetworkCount(res.data.count || 0);
    } catch (error) {
      console.error('Error fetching network count:', error);
    }
  };

  // Filter matches to show nearby ones first
  const nearbyMatches = matches.filter(m => m.is_nearby);
  const otherMatches = matches.filter(m => !m.is_nearby);
  const sortedMatches = [...nearbyMatches, ...otherMatches];

  return (
    <aside className="right-panel" data-testid="right-panel">
      {/* Nearby Homesteaders Section */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <MapPin size={20} weight="fill" className="text-[var(--brand-accent)]" />
          <h3 className="text-lg font-semibold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Nearby Homesteaders
          </h3>
        </div>
        
        {userLocation && (
          <div className="flex items-center gap-2 mb-3 px-2 py-1 bg-[var(--bg-surface)] border border-[var(--border-color)] text-xs text-[var(--text-muted)]">
            <NavigationArrow size={12} className="text-[var(--brand-primary)]" />
            <span>Your location: <span className="text-[var(--text-secondary)]">{userLocation}</span></span>
          </div>
        )}
        
        {loadingNearby ? (
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 text-center">
            <div className="w-5 h-5 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        ) : !userLocation ? (
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 text-center">
            <MapPin size={32} className="mx-auto text-[var(--bg-surface-active)] mb-2" />
            <p className="text-sm text-[var(--text-muted)]">
              Add your location to find nearby homesteaders
            </p>
          </div>
        ) : nearbyUsers.length === 0 ? (
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 text-center">
            <Users size={32} className="mx-auto text-[var(--bg-surface-active)] mb-2" />
            <p className="text-sm text-[var(--text-muted)]">
              No homesteaders found in your area yet
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {nearbyUsers.slice(0, 4).map((user) => (
              <NearbyUserCard key={user._id} user={user} onClick={() => onViewProfile && onViewProfile(user._id)} />
            ))}
          </div>
        )}
      </div>

      {/* Potential Matches Section */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Lightning size={20} weight="fill" className="text-[var(--brand-primary)]" />
          <h3 className="text-lg font-semibold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Potential Matches
          </h3>
        </div>
        
        {sortedMatches.length === 0 ? (
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 text-center">
            <ArrowsLeftRight size={32} className="mx-auto text-[var(--bg-surface-active)] mb-2" />
            <p className="text-sm text-[var(--text-muted)]">
              Update your profile with what you're offering and looking for to see matches
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {sortedMatches.slice(0, 5).map((match) => (
              <MatchCard key={match._id} match={match} onClick={() => onViewProfile && onViewProfile(match.user_id)} />
            ))}
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center gap-2 mb-4">
          <Users size={20} weight="fill" className="text-[var(--brand-accent)]" />
          <h3 className="text-lg font-semibold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Network Stats
          </h3>
        </div>
        
        <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-2xl font-bold text-[var(--brand-primary)]">{networkCount}</p>
              <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider">Network</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--brand-primary)]">{matches.length}</p>
              <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider">Matches</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--brand-accent)]">{nearbyUsers.length}</p>
              <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider">Nearby</p>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-[var(--bg-surface)] border border-[var(--border-color)]">
          <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Encrypted Network</p>
          <p className="text-sm text-[var(--text-secondary)]">
            All messages and sensitive data are encrypted end-to-end for your security.
          </p>
        </div>
      </div>
    </aside>
  );
}

function NearbyUserCard({ user, onClick }) {
  return (
    <div 
      className="bg-[var(--bg-surface)] border border-[var(--border-color)] border-l-2 border-l-[var(--brand-accent)] p-3 card-hover cursor-pointer" 
      data-testid={`nearby-user-${user._id}`}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-accent)] font-semibold shrink-0">
          {user.name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-medium text-[var(--text-primary)] text-sm truncate hover:text-[var(--brand-primary)]">{user.name}</h4>
            {user.is_verified && (
              <span className="verified-badge">
                <SealCheck size={10} weight="fill" />
                Verified Trader
              </span>
            )}
          </div>
          <div className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
            <MapPin size={10} />
            <span className="truncate">{user.location}</span>
          </div>
          {user.skills?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {user.skills.slice(0, 2).map((skill, i) => (
                <span key={`skill-${getItemName(skill)}-${i}`} className="badge text-[10px]">{getItemName(skill)}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MatchCard({ match, onClick }) {
  return (
    <div 
      className="bg-[var(--bg-surface)] border border-[var(--border-color)] border-l-2 border-l-[var(--brand-primary)] p-3 card-hover cursor-pointer" 
      data-testid={`match-${match._id}`}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] font-semibold shrink-0">
          {match.user_name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-medium text-[var(--text-primary)] text-sm truncate">{match.user_name}</h4>
            {match.is_verified && (
              <span className="verified-badge">
                <SealCheck size={10} weight="fill" />
                Verified Trader
              </span>
            )}
            {match.is_nearby && (
              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[var(--brand-accent)]/20 text-[var(--brand-accent)] text-[10px] rounded-full">
                <MapPin size={8} weight="fill" />
                Nearby
              </span>
            )}
          </div>
          <p className="text-xs text-[var(--text-muted)] truncate">{match.title}</p>
          {match.user_location && (
            <div className="flex items-center gap-1 text-[10px] text-[var(--text-muted)] mt-1">
              <MapPin size={8} />
              <span className="truncate">{match.user_location}</span>
            </div>
          )}
          <div className="flex flex-wrap gap-1 mt-2">
            {match.offering?.slice(0, 2).map((item, i) => (
              <span key={`match-offer-${getItemName(item)}-${i}`} className="badge badge-offering text-[10px]">{getItemName(item)}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
