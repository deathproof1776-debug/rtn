import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowsLeftRight, Lightning, Users, MapPin, NavigationArrow } from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function RightPanel({ matches }) {
  const [nearbyUsers, setNearbyUsers] = useState([]);
  const [userLocation, setUserLocation] = useState('');
  const [loadingNearby, setLoadingNearby] = useState(true);

  useEffect(() => {
    fetchNearbyUsers();
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

  // Filter matches to show nearby ones first
  const nearbyMatches = matches.filter(m => m.is_nearby);
  const otherMatches = matches.filter(m => !m.is_nearby);
  const sortedMatches = [...nearbyMatches, ...otherMatches];

  return (
    <aside className="right-panel" data-testid="right-panel">
      {/* Nearby Homesteaders Section */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <MapPin size={20} weight="fill" className="text-[#84CC16]" />
          <h3 className="text-lg font-semibold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Nearby Homesteaders
          </h3>
        </div>
        
        {userLocation && (
          <div className="flex items-center gap-2 mb-3 px-2 py-1 bg-[#1C1917] border border-[#292524] text-xs text-[#78716C]">
            <NavigationArrow size={12} className="text-[#B45309]" />
            <span>Your location: <span className="text-[#A8A29E]">{userLocation}</span></span>
          </div>
        )}
        
        {loadingNearby ? (
          <div className="bg-[#1C1917] border border-[#292524] p-4 text-center">
            <div className="w-5 h-5 border-2 border-[#B45309] border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        ) : !userLocation ? (
          <div className="bg-[#1C1917] border border-[#292524] p-4 text-center">
            <MapPin size={32} className="mx-auto text-[#44403C] mb-2" />
            <p className="text-sm text-[#78716C]">
              Add your location to find nearby homesteaders
            </p>
          </div>
        ) : nearbyUsers.length === 0 ? (
          <div className="bg-[#1C1917] border border-[#292524] p-4 text-center">
            <Users size={32} className="mx-auto text-[#44403C] mb-2" />
            <p className="text-sm text-[#78716C]">
              No homesteaders found in your area yet
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {nearbyUsers.slice(0, 4).map((user) => (
              <NearbyUserCard key={user._id} user={user} />
            ))}
          </div>
        )}
      </div>

      {/* Potential Matches Section */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Lightning size={20} weight="fill" className="text-[#B45309]" />
          <h3 className="text-lg font-semibold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Potential Matches
          </h3>
        </div>
        
        {sortedMatches.length === 0 ? (
          <div className="bg-[#1C1917] border border-[#292524] p-4 text-center">
            <ArrowsLeftRight size={32} className="mx-auto text-[#44403C] mb-2" />
            <p className="text-sm text-[#78716C]">
              Update your profile with what you're offering and looking for to see matches
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {sortedMatches.slice(0, 5).map((match) => (
              <MatchCard key={match._id} match={match} />
            ))}
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center gap-2 mb-4">
          <Users size={20} weight="fill" className="text-[#4D7C0F]" />
          <h3 className="text-lg font-semibold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Network Stats
          </h3>
        </div>
        
        <div className="bg-[#1C1917] border border-[#292524] p-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-2xl font-bold text-[#B45309]">{matches.length}</p>
              <p className="text-xs text-[#78716C] uppercase tracking-wider">Matches</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-[#84CC16]">{nearbyUsers.length}</p>
              <p className="text-xs text-[#78716C] uppercase tracking-wider">Nearby</p>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-[#1C1917] border border-[#292524]">
          <p className="text-xs text-[#78716C] uppercase tracking-wider mb-2">Encrypted Network</p>
          <p className="text-sm text-[#A8A29E]">
            All messages and sensitive data are encrypted end-to-end for your security.
          </p>
        </div>
      </div>
    </aside>
  );
}

function NearbyUserCard({ user }) {
  return (
    <div className="bg-[#1C1917] border border-[#292524] p-3 card-hover" data-testid={`nearby-user-${user._id}`}>
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-[#292524] flex items-center justify-center text-[#84CC16] font-semibold shrink-0">
          {user.name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="font-medium text-[#E7E5E4] text-sm truncate">{user.name}</h4>
          <div className="flex items-center gap-1 text-xs text-[#78716C]">
            <MapPin size={10} />
            <span className="truncate">{user.location}</span>
          </div>
          {user.skills?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {user.skills.slice(0, 2).map((skill, i) => (
                <span key={i} className="badge text-[10px]">{skill}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MatchCard({ match }) {
  return (
    <div className="bg-[#1C1917] border border-[#292524] p-3 card-hover" data-testid={`match-${match._id}`}>
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold shrink-0">
          {match.user_name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-[#E7E5E4] text-sm truncate">{match.user_name}</h4>
            {match.is_nearby && (
              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[#4D7C0F]/20 text-[#84CC16] text-[10px] rounded-full">
                <MapPin size={8} weight="fill" />
                Nearby
              </span>
            )}
          </div>
          <p className="text-xs text-[#78716C] truncate">{match.title}</p>
          {match.user_location && (
            <div className="flex items-center gap-1 text-[10px] text-[#57534E] mt-1">
              <MapPin size={8} />
              <span className="truncate">{match.user_location}</span>
            </div>
          )}
          <div className="flex flex-wrap gap-1 mt-2">
            {match.offering?.slice(0, 2).map((item, i) => (
              <span key={i} className="badge badge-offering text-[10px]">{item}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
