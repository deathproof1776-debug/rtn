import { UserPlus, MapPin, SealCheck, Check, Clock } from '@phosphor-icons/react';

export default function TraderSearchResultCard({ result, onConnect, onViewProfile, isLoading }) {
  const status = result.connection_status;
  return (
    <div
      className="theme-surface border theme-border p-4 hover:border-[var(--brand-primary)]/50 transition-colors"
      data-testid={`search-result-${result.id}`}
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 theme-surface-hover flex items-center justify-center text-[var(--brand-primary)] font-semibold text-lg flex-shrink-0 overflow-hidden">
          {result.avatar ? (
            <img src={result.avatar} alt="" className="w-full h-full object-cover" />
          ) : (
            result.name?.charAt(0)?.toUpperCase() || 'U'
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-0.5">
            <span
              className="font-medium text-[var(--text-primary)] truncate cursor-pointer hover:text-[var(--brand-primary)]"
              onClick={() => onViewProfile && onViewProfile(result.id)}
              data-testid={`search-result-name-${result.id}`}
            >
              {result.name}
            </span>
            {result.is_verified && (
              <span className="verified-badge">
                <SealCheck size={10} weight="fill" />
                Verified
              </span>
            )}
            {result.is_trusted_trader && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-600/20 text-green-500 text-xs rounded-full">
                <SealCheck size={10} weight="fill" />
                Trusted
              </span>
            )}
          </div>
          <p className="text-xs text-[var(--text-muted)] truncate">{result.email}</p>
          {result.location && (
            <p className="text-xs text-[var(--text-muted)] flex items-center gap-1 mt-0.5">
              <MapPin size={12} /> {result.location}
            </p>
          )}
        </div>
        <div className="flex-shrink-0">
          {status === 'connected' ? (
            <span className="inline-flex items-center gap-1 px-3 py-1.5 text-xs text-green-500 border border-green-600/40 rounded" data-testid={`search-status-connected-${result.id}`}>
              <Check size={13} /> Connected
            </span>
          ) : status === 'pending' ? (
            <span className="inline-flex items-center gap-1 px-3 py-1.5 text-xs text-[var(--text-muted)] border border-[var(--border-color)] rounded" data-testid={`search-status-pending-${result.id}`}>
              <Clock size={13} /> Pending
            </span>
          ) : (
            <button
              onClick={() => onConnect(result.id)}
              disabled={isLoading}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs bg-[var(--brand-primary)] text-white rounded hover:opacity-90 disabled:opacity-60"
              data-testid={`search-connect-${result.id}`}
            >
              <UserPlus size={13} /> {isLoading ? 'Sending…' : 'Connect'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
