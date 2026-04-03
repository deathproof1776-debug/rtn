/**
 * RequestCard - Displays incoming/outgoing network requests
 */
import { Check, X, Clock, SealCheck } from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

export function IncomingRequestCard({ 
  request, 
  onAccept, 
  onDecline, 
  isLoading 
}) {
  return (
    <div
      className="theme-surface border border-[var(--brand-primary)]/30 p-4 flex items-center gap-4"
      data-testid={`incoming-request-${request.id}`}
    >
      <div className="w-10 h-10 theme-surface-hover flex items-center justify-center text-[var(--brand-primary)] font-semibold flex-shrink-0">
        {request.from_user_avatar ? (
          <img src={request.from_user_avatar} alt="" className="w-full h-full object-cover" />
        ) : (
          request.from_user_name?.charAt(0)?.toUpperCase() || 'U'
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium text-[var(--text-primary)]">{request.from_user_name}</span>
          {request.is_verified && (
            <span className="verified-badge">
              <SealCheck size={10} weight="fill" />
              Verified
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
          <Clock size={10} />
          {formatDistanceToNow(new Date(request.created_at), { addSuffix: true })}
        </div>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onAccept(request.id)}
          disabled={isLoading}
          className="p-2 bg-[var(--brand-success)]/20 text-[#22C55E] hover:bg-[var(--brand-success)]/30 transition-colors disabled:opacity-50"
          title="Accept"
          data-testid={`accept-request-${request.id}`}
        >
          <Check size={18} weight="bold" />
        </button>
        <button
          onClick={() => onDecline(request.id)}
          disabled={isLoading}
          className="p-2 bg-[var(--brand-danger)]/20 text-[#EF4444] hover:bg-[var(--brand-danger)]/30 transition-colors disabled:opacity-50"
          title="Decline"
          data-testid={`decline-request-${request.id}`}
        >
          <X size={18} weight="bold" />
        </button>
      </div>
    </div>
  );
}

export function OutgoingRequestCard({ 
  request, 
  onCancel, 
  isLoading 
}) {
  return (
    <div
      className="theme-surface border theme-border p-4 flex items-center gap-4"
      data-testid={`outgoing-request-${request.id}`}
    >
      <div className="w-10 h-10 theme-surface-hover flex items-center justify-center text-[var(--brand-primary)] font-semibold flex-shrink-0">
        {request.to_user_avatar ? (
          <img src={request.to_user_avatar} alt="" className="w-full h-full object-cover" />
        ) : (
          request.to_user_name?.charAt(0)?.toUpperCase() || 'U'
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium text-[var(--text-primary)]">{request.to_user_name}</span>
          {request.is_verified && (
            <span className="verified-badge">
              <SealCheck size={10} weight="fill" />
              Verified
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
          <Clock size={10} />
          Sent {formatDistanceToNow(new Date(request.created_at), { addSuffix: true })}
        </div>
      </div>
      <button
        onClick={() => onCancel(request.id)}
        disabled={isLoading}
        className="px-3 py-1.5 text-xs border border-[var(--bg-surface-active)] text-[var(--text-secondary)] hover:border-[var(--brand-danger)] hover:text-[#EF4444] transition-colors disabled:opacity-50"
        data-testid={`cancel-request-${request.id}`}
      >
        Cancel
      </button>
    </div>
  );
}
