import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import {
  ArrowsLeftRight,
  Check,
  X,
  Clock,
  ArrowCounterClockwise,
  PaperPlaneTilt,
  CaretDown,
  CaretUp,
  Handshake,
  Prohibit,
  ClockCounterClockwise,
  Plus,
  Package,
  Tag,
  ChatText
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner';
import CounterTradeModal from './CounterTradeModal';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function TradeDealsPanel() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('incoming');
  const [incoming, setIncoming] = useState([]);
  const [outgoing, setOutgoing] = useState([]);
  const [history, setHistory] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [expandedTrade, setExpandedTrade] = useState(null);
  const [counterModal, setCounterModal] = useState(null);

  useEffect(() => {
    fetchTrades();
  }, []);

  const fetchTrades = async () => {
    setLoading(true);
    try {
      const [inRes, outRes, histRes] = await Promise.all([
        axios.get(`${API_URL}/api/trades/incoming`, { withCredentials: true }),
        axios.get(`${API_URL}/api/trades/outgoing`, { withCredentials: true }),
        axios.get(`${API_URL}/api/trades/history`, { withCredentials: true })
      ]);
      setIncoming(inRes.data);
      setOutgoing(outRes.data);
      setHistory(histRes.data.trades || []);
      setHistoryTotal(histRes.data.total || 0);
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (tradeId, action) => {
    setActionLoading(tradeId);
    try {
      await axios.post(`${API_URL}/api/trades/${tradeId}/respond`, { action }, { withCredentials: true });
      toast.success(`Trade ${action === 'accept' ? 'accepted' : 'declined'}`);
      await fetchTrades();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to respond');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancel = async (tradeId) => {
    setActionLoading(tradeId);
    try {
      await axios.post(`${API_URL}/api/trades/${tradeId}/cancel`, {}, { withCredentials: true });
      toast.success('Trade offer cancelled');
      await fetchTrades();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to cancel');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCounterSubmitted = () => {
    setCounterModal(null);
    fetchTrades();
  };

  const tabs = [
    { id: 'incoming', label: 'Incoming', count: incoming.length },
    { id: 'outgoing', label: 'Outgoing', count: outgoing.length },
    { id: 'history', label: 'History', count: historyTotal },
  ];

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

  const renderTradeCard = (trade, type) => {
    const isExpanded = expandedTrade === trade._id;
    const isIncoming = type === 'incoming';
    const otherName = isIncoming ? trade.proposer_name : trade.receiver_name;
    const counterOffers = trade.counter_offers || [];
    const lastCounter = counterOffers.length > 0 ? counterOffers[counterOffers.length - 1] : null;

    // Determine current terms
    const currentOffering = lastCounter ? lastCounter.offering : trade.offering;
    const currentRequesting = lastCounter ? lastCounter.requesting : trade.requesting;

    // Can this user respond?
    const canRespond = isIncoming && trade.status === 'pending';
    const canRespondToCounter = trade.status === 'countered' && lastCounter && lastCounter.by_user_id !== user?.id;

    return (
      <div
        key={trade._id}
        className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] border-l-3 mb-3"
        style={{ borderLeftWidth: '3px', borderLeftColor: isIncoming ? 'var(--brand-primary)' : 'var(--brand-accent)' }}
        data-testid={`trade-card-${trade._id}`}
      >
        {/* Card Header */}
        <div
          className="flex items-center justify-between p-4 cursor-pointer hover:bg-[var(--bg-surface-hover)] transition-colors"
          onClick={() => setExpandedTrade(isExpanded ? null : trade._id)}
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
                    <span key={`offer-${item}-${i}`} className="badge badge-offering text-xs">{item}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wider text-[var(--brand-primary)] font-semibold mb-1.5 flex items-center gap-1">
                  <Tag size={14} /> Requesting
                </p>
                <div className="flex flex-wrap gap-1">
                  {currentRequesting.map((item, i) => (
                    <span key={`req-${item}-${i}`} className="badge badge-looking text-xs">{item}</span>
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
                              <span key={`co-offer-${item}-${i}`} className="text-[10px] px-1.5 py-0.5 bg-[rgba(77,124,15,0.15)] text-[var(--brand-accent)] border border-[var(--brand-accent)]">{item}</span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase text-[var(--brand-primary)]">Requesting</p>
                          <div className="flex flex-wrap gap-1 mt-0.5">
                            {co.requesting.map((item, i) => (
                              <span key={`co-req-${item}-${i}`} className="text-[10px] px-1.5 py-0.5 bg-[rgba(180,83,9,0.15)] text-[var(--brand-primary)] border border-[var(--brand-primary)]">{item}</span>
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
                  onClick={() => handleRespond(trade._id, 'accept')}
                  disabled={actionLoading === trade._id}
                  className="btn-primary flex items-center gap-1.5 text-sm px-4 py-2"
                  data-testid={`accept-trade-${trade._id}`}
                >
                  <Check size={16} weight="bold" /> Accept
                </button>
                <button
                  onClick={() => setCounterModal(trade)}
                  disabled={actionLoading === trade._id}
                  className="btn-secondary flex items-center gap-1.5 text-sm px-4 py-2"
                  data-testid={`counter-trade-${trade._id}`}
                >
                  <ArrowCounterClockwise size={16} /> Counter
                </button>
                <button
                  onClick={() => handleRespond(trade._id, 'decline')}
                  disabled={actionLoading === trade._id}
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
                {trade.status === 'countered' && lastCounter && lastCounter.by_user_id !== user?.id && (
                  <>
                    <button
                      onClick={() => handleRespond(trade._id, 'accept')}
                      disabled={actionLoading === trade._id}
                      className="btn-primary flex items-center gap-1.5 text-sm px-4 py-2"
                      data-testid={`accept-counter-${trade._id}`}
                    >
                      <Check size={16} weight="bold" /> Accept Counter
                    </button>
                    <button
                      onClick={() => setCounterModal(trade)}
                      disabled={actionLoading === trade._id}
                      className="btn-secondary flex items-center gap-1.5 text-sm px-4 py-2"
                      data-testid={`re-counter-trade-${trade._id}`}
                    >
                      <ArrowCounterClockwise size={16} /> Counter
                    </button>
                  </>
                )}
                <button
                  onClick={() => handleCancel(trade._id)}
                  disabled={actionLoading === trade._id}
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
  };

  const renderHistoryCard = (trade) => {
    const isProposer = trade.proposer_id === user?.id;
    const otherName = isProposer ? trade.receiver_name : trade.proposer_name;

    return (
      <div
        key={trade._id}
        className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] p-4 mb-3 opacity-80"
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
            {trade.status}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-[var(--brand-accent)] mb-1">Offering</p>
            <div className="flex flex-wrap gap-1">
              {trade.offering.map((item, i) => (
                <span key={`hist-offer-${item}-${i}`} className="badge badge-offering text-xs">{item}</span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-[var(--brand-primary)] mb-1">Requesting</p>
            <div className="flex flex-wrap gap-1">
              {trade.requesting.map((item, i) => (
                <span key={`hist-req-${item}-${i}`} className="badge badge-looking text-xs">{item}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-3xl mx-auto" data-testid="trade-deals-panel">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <ArrowsLeftRight size={28} weight="duotone" className="text-[var(--brand-primary)]" />
          <h1 className="text-2xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Trade Deals
          </h1>
        </div>
        <p className="text-sm text-[var(--text-muted)]">Manage your trade offers, counter-offers, and deal history</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[var(--border-color)] mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-sm font-medium transition-colors relative ${
              activeTab === tab.id
                ? 'text-[var(--brand-primary)]'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
            data-testid={`trade-tab-${tab.id}`}
          >
            <span className="flex items-center gap-1.5">
              {tab.label}
              {tab.count > 0 && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full min-w-[18px] text-center ${
                  activeTab === tab.id ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--bg-surface-hover)] text-[var(--text-muted)]'
                }`}>
                  {tab.count}
                </span>
              )}
            </span>
            {activeTab === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--brand-primary)]" />
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="text-[var(--text-muted)]">Loading trades...</div>
        </div>
      ) : (
        <>
          {activeTab === 'incoming' && (
            <div data-testid="incoming-trades-list">
              {incoming.length === 0 ? (
                <EmptyState
                  icon={<Handshake size={40} className="text-[var(--text-muted)]" />}
                  title="No incoming offers"
                  subtitle="Trade offers from other members will appear here"
                />
              ) : (
                incoming.map((trade) => renderTradeCard(trade, 'incoming'))
              )}
            </div>
          )}

          {activeTab === 'outgoing' && (
            <div data-testid="outgoing-trades-list">
              {outgoing.length === 0 ? (
                <EmptyState
                  icon={<PaperPlaneTilt size={40} className="text-[var(--text-muted)]" />}
                  title="No outgoing offers"
                  subtitle="Trade offers you've sent will appear here"
                />
              ) : (
                outgoing.map((trade) => renderTradeCard(trade, 'outgoing'))
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div data-testid="trade-history-list">
              {history.length === 0 ? (
                <EmptyState
                  icon={<ClockCounterClockwise size={40} className="text-[var(--text-muted)]" />}
                  title="No trade history"
                  subtitle="Completed, declined, or cancelled trades will show here"
                />
              ) : (
                history.map((trade) => renderHistoryCard(trade))
              )}
            </div>
          )}
        </>
      )}

      {/* Counter-offer Modal */}
      {counterModal && (
        <CounterTradeModal
          trade={counterModal}
          onClose={() => setCounterModal(null)}
          onCounterSubmitted={handleCounterSubmitted}
        />
      )}
    </div>
  );
}

function EmptyState({ icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center" data-testid="empty-state">
      {icon}
      <p className="text-[var(--text-primary)] font-medium mt-3">{title}</p>
      <p className="text-sm text-[var(--text-muted)] mt-1">{subtitle}</p>
    </div>
  );
}
