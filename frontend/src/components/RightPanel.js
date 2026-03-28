import { ArrowsLeftRight, Lightning, Users } from '@phosphor-icons/react';

export default function RightPanel({ matches }) {
  return (
    <aside className="right-panel" data-testid="right-panel">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Lightning size={20} weight="fill" className="text-[#B45309]" />
          <h3 className="text-lg font-semibold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Potential Matches
          </h3>
        </div>
        
        {matches.length === 0 ? (
          <div className="bg-[#1C1917] border border-[#292524] p-4 text-center">
            <ArrowsLeftRight size={32} className="mx-auto text-[#44403C] mb-2" />
            <p className="text-sm text-[#78716C]">
              Update your profile with what you're offering and looking for to see matches
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {matches.slice(0, 5).map((match) => (
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
              <p className="text-2xl font-bold text-[#4D7C0F]">Active</p>
              <p className="text-xs text-[#78716C] uppercase tracking-wider">Status</p>
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

function MatchCard({ match }) {
  return (
    <div className="bg-[#1C1917] border border-[#292524] p-3 card-hover" data-testid={`match-${match._id}`}>
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold shrink-0">
          {match.user_name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="font-medium text-[#E7E5E4] text-sm truncate">{match.user_name}</h4>
          <p className="text-xs text-[#78716C] truncate">{match.title}</p>
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
