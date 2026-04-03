/**
 * TradeDealsPanel - Manage trade offers, counter-offers, and deal history
 * Refactored to use modular sub-components
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import {
  ArrowsLeftRight,
  Handshake,
  PaperPlaneTilt,
  ClockCounterClockwise
} from '@phosphor-icons/react';
import { toast } from 'sonner';
import CounterTradeModal from './CounterTradeModal';

import { TradeCard, HistoryCard, EmptyState } from './trades';

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

  const toggleExpand = (tradeId) => {
    setExpandedTrade(expandedTrade === tradeId ? null : tradeId);
  };

  const tabs = [
    { id: 'incoming', label: 'Incoming', count: incoming.length },
    { id: 'outgoing', label: 'Outgoing', count: outgoing.length },
    { id: 'history', label: 'History', count: historyTotal },
  ];

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
                incoming.map((trade) => (
                  <TradeCard
                    key={trade._id}
                    trade={trade}
                    type="incoming"
                    currentUserId={user?.id}
                    isExpanded={expandedTrade === trade._id}
                    onToggleExpand={toggleExpand}
                    onAccept={(id) => handleRespond(id, 'accept')}
                    onDecline={(id) => handleRespond(id, 'decline')}
                    onCounter={setCounterModal}
                    onCancel={handleCancel}
                    isLoading={actionLoading === trade._id}
                  />
                ))
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
                outgoing.map((trade) => (
                  <TradeCard
                    key={trade._id}
                    trade={trade}
                    type="outgoing"
                    currentUserId={user?.id}
                    isExpanded={expandedTrade === trade._id}
                    onToggleExpand={toggleExpand}
                    onAccept={(id) => handleRespond(id, 'accept')}
                    onDecline={(id) => handleRespond(id, 'decline')}
                    onCounter={setCounterModal}
                    onCancel={handleCancel}
                    isLoading={actionLoading === trade._id}
                  />
                ))
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
                history.map((trade) => (
                  <HistoryCard 
                    key={trade._id} 
                    trade={trade} 
                    currentUserId={user?.id} 
                  />
                ))
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
