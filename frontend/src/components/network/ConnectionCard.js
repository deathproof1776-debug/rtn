/**
 * ConnectionCard - Displays a network connection with removal option
 */
import { UserMinus, MapPin, SealCheck } from '@phosphor-icons/react';

// Helper to get display name from item (handles both string and object formats)
const getItemName = (item) => {
  if (typeof item === 'string') return item;
  return item?.name || '';
};

export default function ConnectionCard({ 
  connection, 
  onRemove, 
  onViewProfile, 
  isLoading 
}) {
  return (
    <div
      className="theme-surface border theme-border p-4 flex items-center gap-4 hover:border-[var(--brand-primary)]/30 transition-colors"
      data-testid={`connection-${connection.id}`}
    >
      <div className="w-12 h-12 theme-surface-hover flex items-center justify-center text-[var(--brand-primary)] font-semibold text-lg flex-shrink-0">
        {connection.avatar ? (
          <img src={connection.avatar} alt="" className="w-full h-full object-cover" />
        ) : (
          connection.name?.charAt(0)?.toUpperCase() || 'U'
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span 
            className="font-medium text-[var(--text-primary)] truncate cursor-pointer hover:text-[var(--brand-primary)]"
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
          <div className="flex items-center gap-1 text-xs text-[var(--text-muted)] mt-0.5">
            <MapPin size={10} />
            {connection.location}
          </div>
        )}
        {connection.skills?.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {connection.skills.slice(0, 3).map((skill, i) => (
              <span key={`skill-${getItemName(skill)}-${i}`} className="text-[10px] px-1.5 py-0.5 theme-surface-hover theme-text-secondary">
                {getItemName(skill)}
              </span>
            ))}
            {connection.skills.length > 3 && (
              <span className="text-[10px] text-[var(--text-muted)]">+{connection.skills.length - 3}</span>
            )}
          </div>
        )}
      </div>
      <button
        onClick={() => onRemove(connection.id)}
        disabled={isLoading}
        className="p-2 text-[var(--brand-danger)] hover:bg-[var(--brand-danger)]/10 transition-colors disabled:opacity-50"
        title="Remove from network"
        data-testid={`remove-connection-${connection.id}`}
      >
        <UserMinus size={20} />
      </button>
    </div>
  );
}
