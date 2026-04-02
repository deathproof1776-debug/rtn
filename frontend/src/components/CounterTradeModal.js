import { useState } from 'react';
import axios from 'axios';
import { X, ArrowCounterClockwise, Plus, PaperPlaneTilt } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CounterTradeModal({ trade, onClose, onCounterSubmitted }) {
  const lastCounter = trade.counter_offers?.length > 0 ? trade.counter_offers[trade.counter_offers.length - 1] : null;
  const currentOffering = lastCounter ? lastCounter.offering : trade.offering;
  const currentRequesting = lastCounter ? lastCounter.requesting : trade.requesting;

  const [offering, setOffering] = useState([...currentRequesting]);
  const [requesting, setRequesting] = useState([...currentOffering]);
  const [offeringInput, setOfferingInput] = useState('');
  const [requestingInput, setRequestingInput] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const addItem = (type) => {
    const input = type === 'offering' ? offeringInput.trim() : requestingInput.trim();
    if (!input) return;
    if (type === 'offering') {
      if (!offering.includes(input)) setOffering([...offering, input]);
      setOfferingInput('');
    } else {
      if (!requesting.includes(input)) setRequesting([...requesting, input]);
      setRequestingInput('');
    }
  };

  const removeItem = (type, item) => {
    if (type === 'offering') setOffering(offering.filter(i => i !== item));
    else setRequesting(requesting.filter(i => i !== item));
  };

  const handleKeyDown = (e, type) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addItem(type);
    }
  };

  const handleSubmit = async () => {
    if (offering.length === 0 || requesting.length === 0) {
      toast.error('Both offering and requesting items are required');
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/api/trades/${trade._id}/counter`, {
        offering,
        requesting,
        message
      }, { withCredentials: true });
      toast.success('Counter-offer sent!');
      onCounterSubmitted?.();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send counter-offer');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="counter-trade-modal">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)]">
          <div className="flex items-center gap-2">
            <ArrowCounterClockwise size={22} weight="duotone" className="text-[var(--brand-primary)]" />
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Counter-Offer</h2>
          </div>
          <button onClick={onClose} className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]" data-testid="close-counter-modal">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-5">
          {/* Offering */}
          <div>
            <label className="text-xs uppercase tracking-wider text-[var(--brand-accent)] font-semibold mb-2 block">
              You are offering
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={offeringInput}
                onChange={(e) => setOfferingInput(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'offering')}
                placeholder="Add item..."
                className="input-field flex-1 text-sm"
                data-testid="counter-offering-input"
              />
              <button onClick={() => addItem('offering')} className="btn-secondary px-3" data-testid="counter-add-offering-btn">
                <Plus size={16} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {offering.map((item) => (
                <span key={item} className="badge badge-offering flex items-center gap-1">
                  {item}
                  <button onClick={() => removeItem('offering', item)}><X size={12} /></button>
                </span>
              ))}
            </div>
          </div>

          {/* Requesting */}
          <div>
            <label className="text-xs uppercase tracking-wider text-[var(--brand-primary)] font-semibold mb-2 block">
              You are requesting
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={requestingInput}
                onChange={(e) => setRequestingInput(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'requesting')}
                placeholder="Add item..."
                className="input-field flex-1 text-sm"
                data-testid="counter-requesting-input"
              />
              <button onClick={() => addItem('requesting')} className="btn-secondary px-3" data-testid="counter-add-requesting-btn">
                <Plus size={16} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {requesting.map((item) => (
                <span key={item} className="badge badge-looking flex items-center gap-1">
                  {item}
                  <button onClick={() => removeItem('requesting', item)}><X size={12} /></button>
                </span>
              ))}
            </div>
          </div>

          {/* Message */}
          <div>
            <label className="text-xs uppercase tracking-wider text-[var(--text-muted)] font-semibold mb-2 block">
              Message (optional)
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Explain your counter-offer..."
              className="input-field w-full text-sm resize-none"
              rows={3}
              data-testid="counter-message-input"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={submitting || offering.length === 0 || requesting.length === 0}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            data-testid="submit-counter-btn"
          >
            <PaperPlaneTilt size={18} weight="bold" />
            {submitting ? 'Sending...' : 'Send Counter-Offer'}
          </button>
        </div>
      </div>
    </div>
  );
}
