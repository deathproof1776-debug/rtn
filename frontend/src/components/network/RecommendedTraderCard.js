/**
 * RecommendedTraderCard - Displays a recommended trader with match reasons
 */
import { UserPlus, MapPin, SealCheck } from '@phosphor-icons/react';

export default function RecommendedTraderCard({ 
  recommendation, 
  onConnect, 
  onViewProfile, 
  isLoading 
}) {
  return (
    <div
      className="theme-surface border theme-border border-l-2 border-l-[#F59E0B] p-4 hover:border-[#F59E0B]/50 transition-colors"
      data-testid={`recommended-${recommendation.id}`}
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 theme-surface-hover flex items-center justify-center text-[#F59E0B] font-semibold text-lg flex-shrink-0">
          {recommendation.avatar ? (
            <img src={recommendation.avatar} alt="" className="w-full h-full object-cover" />
          ) : (
            recommendation.name?.charAt(0)?.toUpperCase() || 'U'
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span 
              className="font-medium text-[var(--text-primary)] truncate cursor-pointer hover:text-[#F59E0B]"
              onClick={() => onViewProfile && onViewProfile(recommendation.id)}
            >
              {recommendation.name}
            </span>
            {recommendation.is_verified && (
              <span className="verified-badge">
                <SealCheck size={10} weight="fill" />
                Verified
              </span>
            )}
          </div>
          {recommendation.location && (
            <div className="flex items-center gap-1 text-xs text-[var(--text-muted)] mb-2">
              <MapPin size={10} />
              {recommendation.location}
            </div>
          )}
          {/* Match reason */}
          <div className="text-xs text-[#F59E0B] mb-2 font-medium">
            {recommendation.reason}
          </div>
          {/* What they offer that you want */}
          {recommendation.offers_you_want?.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-1">
              {recommendation.offers_you_want.map((item, i) => (
                <span key={`offers-${item}-${i}`} className="text-[10px] px-1.5 py-0.5 bg-[var(--brand-success)]/20 text-[#22C55E] border border-[var(--brand-success)]/30">
                  Offers: {item}
                </span>
              ))}
            </div>
          )}
          {/* What they want that you offer */}
          {recommendation.wants_you_offer?.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {recommendation.wants_you_offer.map((item, i) => (
                <span key={`wants-${item}-${i}`} className="text-[10px] px-1.5 py-0.5 bg-[var(--brand-primary)]/20 text-[#F59E0B] border border-[var(--brand-primary)]/30">
                  Wants: {item}
                </span>
              ))}
            </div>
          )}
        </div>
        <button
          onClick={() => onConnect(recommendation.id)}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-2 bg-[#F59E0B] text-black text-sm font-medium hover:bg-[var(--brand-primary-hover)] transition-colors disabled:opacity-50 flex-shrink-0"
          data-testid={`add-recommended-${recommendation.id}`}
        >
          <UserPlus size={16} />
          <span className="hidden sm:inline">Connect</span>
        </button>
      </div>
    </div>
  );
}
