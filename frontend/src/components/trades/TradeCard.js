/**
 * TradeCard - Displays an active trade deal (incoming or outgoing)
 */
import {
  Check,
  X,
  Clock,
  ArrowCounterClockwise,
  CaretDown,
  CaretUp,
  Prohibit,
  Package,
  Tag,
  ChatText
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

// Helper to get display name from item (handles both string and object formats)
const getItemName = (item) => {
  if (typeof item === 'string') return item;
  return item?.name || '';
};

const getStatusStyle = (status) => {
  switch (status) {
    case 'accepted': return 'text-[var(--brand-accent)] bg-[rgba(77,124,15,0.15)] border-[var(--brand-accent)]';
    case 'declined': return 'text-[var(--brand-danger)] bg-[rgba(153,27,27,0.15)] border-[var(--brand-danger)]';
    case 'cancelled': return 'text-[var(--text-muted)] bg-[var(--bg-surface-hover)] border-[var(--bg-surface-active)]';
    case 'countered': return 'text-[var(--brand-primary)] bg-[rgba(180,83,9,0.15)] border-[var(--brand-primary)]';
    default: return 'text-[var(--text-secondary)] bg-[var(--bg-surface-hover)] border-[var(--bg-surface-active)]';
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case 'accepted': return <Check size={12} weight="bold" />;
    case 'declined': return <Prohibit size={12} />;
    case 'cancelled': return <X size={12} />;
    case 'countered': return <ArrowCounterClockwise size={12} />;
    default: return <Clock size={12} />;
  }
};

export default function TradeCard({
  trade,
  type,
  currentUserId,
  isExpanded,
  onToggleExpand,
  onAccept,
  onDecline,
  onCounter,
  onCancel,
  isLoading
}) {
  const isIncoming = type === 'incoming';
  const otherName = isIncoming ? trade.proposer_name : trade.receiver_name;
  const counterOffers = trade.counter_offers || [];
  const lastCounter = counterOffers.length > 0 ? counterOffers[counterOffers.length - 1] : null;

  // Determine current terms
  const currentOffering = lastCounter ? lastCounter.offering : trade.offering;
  const currentRequesting = lastCounter ? lastCounter.requesting : trade.requesting;

  // Can this user respond?
  const canRespond = isIncoming && trade.status === 'pending';
  const canRespondToCounter = trade.status === 'countered' && lastCounter && lastCounter.by_user_id !== currentUserId;

  return (
    <div
      className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] border-l-3 mb-3"
      style={{ borderLeftWidth: '3px', borderLeftColor: isIncoming ? 'var(--brand-primary)' : 'var(--brand-accent)' }}
      data-testid={`trade-card-${trade._id}`}
    >
      {/* Card Header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-[var(--bg-surface-hover)] transition-colors"
        onClick={() => onToggleExpand(trade._id)}
        data-testid={`trade-card-toggle-${trade._id}`}
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 bg-[var(--bg-surface-hover)] border border-[var(--bg-surface-active)] flex items-center justify-center text-[var(--brand-primary)] font-semibold text-sm flex-shrink-0">
            {otherName?.charAt(0)?.toUpperCase() || '?'}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-[var(--text-primary)] truncate">
              {isIncoming ? `From ${otherName}` : `To ${otherName}`}
            </p>
            <p className="text-xs text-[var(--text-muted)]">
              {formatDistanceToNow(new Date(trade.updated_at || trade.created_at), { addSuffix: true })}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 border ${getStatusStyle(trade.status)}`}>
            {getStatusIcon(trade.status)}
            {trade.status}
          </span>
          {isExpanded ? <CaretUp size={16} className="text-[var(--text-muted)]" /> : <CaretDown size={16} className="text-[var(--text-muted)]" />}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-[var(--border-color)] p-4 space-y-4" data-testid={`trade-card-details-${trade._id}`}>
          {/* Current Terms */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--brand-accent)] font-semibold mb-1.5 flex items-center gap-1">
                <Package size={14} /> Offering
              </p>
              <div className="flex flex-wrap gap-1">
                {currentOffering.map((item, i) => (
                  <span key={`offer-${getItemName(item)}-${i}`} className="badge badge-offering text-xs">{getItemName(item)}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--brand-primary)] font-semibold mb-1.5 flex items-center gap-1">
                <Tag size={14} /> Requesting
              </p>
              <div className="flex flex-wrap gap-1">
                {currentRequesting.map((item, i) => (
                  <span key={`req-${getItemName(item)}-${i}`} className="badge badge-looking text-xs">{getItemName(item)}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Message */}
          {trade.message && (
            <div className="bg-[var(--bg-main)] border border-[var(--border-color)] p-3">
              <p className="text-xs text-[var(--text-muted)] mb-1 flex items-center gap-1">
                <ChatText size={12} /> Message
              </p>
              <p className="text-sm text-[var(--text-secondary)]">{trade.message}</p>
            </div>
          )}

          {/* Counter Offer History */}
          {counterOffers.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--text-muted)] font-semibold mb-2">
                Counter-Offer History ({counterOffers.length})
              </p>
              <div className="space-y-2">
                {counterOffers.map((co, idx) => (
                  <div key={co.id || idx} className="bg-[var(--bg-main)] border border-[var(--border-color)] p-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs font-medium text-[var(--text-primary)]">
                        {co.by_user_name}
                      </p>
                      <p className="text-xs text-[var(--text-muted)]">
                        {formatDistanceToNow(new Date(co.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <p className="text-[10px] uppercase text-[var(--brand-accent)]">Offering</p>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {co.offering.map((item, i) => (
                            <span key={`co-offer-${getItemName(item)}-${i}`} className="text-[10px] px-1.5 py-0.5 bg-[rgba(77,124,15,0.15)] text-[var(--brand-accent)] border border-[var(--brand-accent)]">{getItemName(item)}</span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase text-[var(--brand-primary)]">Requesting</p>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {co.requesting.map((item, i) => (
                            <span key={`co-req-${getItemName(item)}-${i}`} className="text-[10px] px-1.5 py-0.5 bg-[rgba(180,83,9,0.15)] text-[var(--brand-primary)] border border-[var(--brand-primary)]">{getItemName(item)}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                    {co.message && <p className="text-xs text-[var(--text-muted)] mt-1.5 italic">"{co.message}"</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          {(canRespond || canRespondToCounter) && (
            <div className="flex flex-wrap gap-2 pt-1">
              <button
                onClick={() => onAccept(trade._id)}
                disabled={isLoading}
                className="btn-primary flex items-center gap-1.5 text-sm px-4 py-2"
                data-testid={`accept-trade-${trade._id}`}
              >
                <Check size={16} weight="bold" /> Accept
              </button>
              <button
                onClick={() => onCounter(trade)}
                disabled={isLoading}
                className="btn-secondary flex items-center gap-1.5 text-sm px-4 py-2"
                data-testid={`counter-trade-${trade._id}`}
              >
                <ArrowCounterClockwise size={16} /> Counter
              </button>
              <button
                onClick={() => onDecline(trade._id)}
                disabled={isLoading}
                className="btn-ghost flex items-center gap-1.5 text-sm px-4 py-2 text-[var(--brand-danger)]"
                data-testid={`decline-trade-${trade._id}`}
              >
                <X size={16} /> Decline
              </button>
            </div>
          )}

          {/* Cancel button for proposer on pending/countered */}
          {type === 'outgoing' && ['pending', 'countered'].includes(trade.status) && (
            <div className="flex gap-2 pt-1">
              {trade.status === 'countered' && lastCounter && lastCounter.by_user_id !== currentUserId && (
                <>
                  <button
                    onClick={() => onAccept(trade._id)}
                    disabled={isLoading}
                    className="btn-primary flex items-center gap-1.5 text-sm px-4 py-2"
                    data-testid={`accept-counter-${trade._id}`}
                  >
                    <Check size={16} weight="bold" /> Accept Counter
                  </button>
                  <button
                    onClick={() => onCounter(trade)}
                    disabled={isLoading}
                    className="btn-secondary flex items-center gap-1.5 text-sm px-4 py-2"
                    data-testid={`re-counter-trade-${trade._id}`}
                  >
                    <ArrowCounterClockwise size={16} /> Counter
                  </button>
                </>
              )}
              <button
                onClick={() => onCancel(trade._id)}
                disabled={isLoading}
                className="btn-ghost flex items-center gap-1.5 text-sm px-4 py-2 text-[var(--brand-danger)]"
                data-testid={`cancel-trade-${trade._id}`}
              >
                <Prohibit size={16} /> Cancel Trade
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
