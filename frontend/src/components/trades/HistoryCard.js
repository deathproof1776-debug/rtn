/**
 * HistoryCard - Displays a completed/closed trade deal
 */
import { Check, X, Clock, ArrowCounterClockwise, Prohibit, CheckCircle, Handshake } from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

// Helper to get display name from item (handles both string and object formats)
const getItemName = (item) => {
  if (typeof item === 'string') return item;
  return item?.name || '';
};

const getStatusStyle = (status) => {
  switch (status) {
    case 'completed': return 'text-green-500 bg-green-900/20 border-green-600';
    case 'accepted': return 'text-[var(--brand-accent)] bg-[rgba(77,124,15,0.15)] border-[var(--brand-accent)]';
    case 'declined': return 'text-[var(--brand-danger)] bg-[rgba(153,27,27,0.15)] border-[var(--brand-danger)]';
    case 'cancelled': return 'text-[var(--text-muted)] bg-[var(--bg-surface-hover)] border-[var(--bg-surface-active)]';
    case 'countered': return 'text-[var(--brand-primary)] bg-[rgba(180,83,9,0.15)] border-[var(--brand-primary)]';
    default: return 'text-[var(--text-secondary)] bg-[var(--bg-surface-hover)] border-[var(--bg-surface-active)]';
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case 'completed': return <CheckCircle size={12} weight="fill" />;
    case 'accepted': return <Check size={12} weight="bold" />;
    case 'declined': return <Prohibit size={12} />;
    case 'cancelled': return <X size={12} />;
    case 'countered': return <ArrowCounterClockwise size={12} />;
    default: return <Clock size={12} />;
  }
};

const getStatusLabel = (status) => {
  switch (status) {
    case 'completed': return 'Completed';
    case 'accepted': return 'Awaiting Confirmation';
    default: return status;
  }
};

export default function HistoryCard({ trade, currentUserId, onConfirmComplete, confirming }) {
  const isProposer = trade.proposer_id === currentUserId;
  const otherName = isProposer ? trade.receiver_name : trade.proposer_name;
  
  // Check if this user has already confirmed
  const userConfirmed = isProposer ? trade.proposer_confirmed : trade.receiver_confirmed;
  const otherConfirmed = isProposer ? trade.receiver_confirmed : trade.proposer_confirmed;
  
  // Show confirm button only for accepted trades that user hasn't confirmed yet
  const showConfirmButton = trade.status === 'accepted' && !userConfirmed;

  return (
    <div
      className={`bg-[var(--bg-surface)] border p-4 mb-3 ${trade.status === 'completed' ? 'border-green-600/30' : 'border-[var(--bg-surface-active)] opacity-80'}`}
      data-testid={`history-card-${trade._id}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[var(--bg-surface-hover)] border border-[var(--bg-surface-active)] flex items-center justify-center text-[var(--text-muted)] font-semibold text-sm">
            {otherName?.charAt(0)?.toUpperCase() || '?'}
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--text-primary)]">
              {isProposer ? `To ${otherName}` : `From ${otherName}`}
            </p>
            <p className="text-xs text-[var(--text-muted)]">
              {trade.completed_at ? formatDistanceToNow(new Date(trade.completed_at), { addSuffix: true }) : formatDistanceToNow(new Date(trade.created_at), { addSuffix: true })}
            </p>
          </div>
        </div>
        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 border ${getStatusStyle(trade.status)}`}>
          {getStatusIcon(trade.status)}
          {getStatusLabel(trade.status)}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-[var(--brand-accent)] mb-1">Offering</p>
          <div className="flex flex-wrap gap-1">
            {trade.offering.map((item, i) => (
              <span key={`hist-offer-${getItemName(item)}-${i}`} className="badge badge-offering text-xs">{getItemName(item)}</span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wider text-[var(--brand-primary)] mb-1">Requesting</p>
          <div className="flex flex-wrap gap-1">
            {trade.requesting.map((item, i) => (
              <span key={`hist-req-${getItemName(item)}-${i}`} className="badge badge-looking text-xs">{getItemName(item)}</span>
            ))}
          </div>
        </div>
      </div>
      
      {/* Confirmation Status for Accepted Trades */}
      {trade.status === 'accepted' && (
        <div className="mt-4 pt-3 border-t border-[var(--border-color)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 text-xs">
              <span className={`flex items-center gap-1 ${userConfirmed ? 'text-green-500' : 'text-[var(--text-muted)]'}`}>
                {userConfirmed ? <CheckCircle size={14} weight="fill" /> : <Clock size={14} />}
                You: {userConfirmed ? 'Confirmed' : 'Pending'}
              </span>
              <span className={`flex items-center gap-1 ${otherConfirmed ? 'text-green-500' : 'text-[var(--text-muted)]'}`}>
                {otherConfirmed ? <CheckCircle size={14} weight="fill" /> : <Clock size={14} />}
                {otherName}: {otherConfirmed ? 'Confirmed' : 'Pending'}
              </span>
            </div>
            
            {showConfirmButton && (
              <button
                onClick={() => onConfirmComplete(trade._id)}
                disabled={confirming}
                className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1"
                data-testid={`confirm-trade-${trade._id}`}
              >
                <Handshake size={14} weight="bold" />
                {confirming ? 'Confirming...' : 'Confirm Completed'}
              </button>
            )}
          </div>
          
          {userConfirmed && !otherConfirmed && (
            <p className="text-xs text-[var(--text-muted)] mt-2">
              Waiting for {otherName} to confirm the trade was completed.
            </p>
          )}
        </div>
      )}
      
      {/* Completed Badge */}
      {trade.status === 'completed' && (
        <div className="mt-3 pt-3 border-t border-green-600/30 flex items-center gap-2 text-green-500 text-xs">
          <CheckCircle size={16} weight="fill" />
          <span>Both parties confirmed - Trade successfully completed!</span>
        </div>
      )}
    </div>
  );
}
