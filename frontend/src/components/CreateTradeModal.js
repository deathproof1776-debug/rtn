import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { X, ArrowsLeftRight, Plus, PaperPlaneTilt } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CreateTradeModal({ onClose, receiverId, receiverName, postId = null, onTradeCreated, initialOffering = [], initialRequesting = [] }) {
  const { user } = useAuth();
  const [offering, setOffering] = useState(initialOffering);
  const [requesting, setRequesting] = useState(initialRequesting);
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
    if (offering.length === 0) {
      toast.error('Add at least one item you are offering');
      return;
    }
    if (requesting.length === 0) {
      toast.error('Add at least one item you are requesting');
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/api/trades`, {
        receiver_id: receiverId,
        offering,
        requesting,
        message,
        post_id: postId
      }, { withCredentials: true });
      toast.success('Trade offer sent!');
      onTradeCreated?.();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send trade offer');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="create-trade-modal">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)]">
          <div className="flex items-center gap-2">
            <ArrowsLeftRight size={22} weight="duotone" className="text-[var(--brand-primary)]" />
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Propose Trade</h2>
          </div>
          <button onClick={onClose} className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]" data-testid="close-trade-modal">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-5">
          {/* Trading with */}
          <div>
            <p className="text-xs uppercase tracking-wider text-[var(--text-muted)] mb-1">Trading with</p>
            <p className="text-[var(--text-primary)] font-medium">{receiverName}</p>
          </div>

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
                placeholder="e.g., 2 dozen eggs"
                className="input-field flex-1 text-sm"
                data-testid="trade-offering-input"
              />
              <button
                onClick={() => addItem('offering')}
                className="btn-secondary px-3 flex items-center gap-1 text-sm"
                data-testid="add-offering-btn"
              >
                <Plus size={16} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {offering.map((item) => (
                <span key={item} className="badge badge-offering flex items-center gap-1" data-testid="offering-tag">
                  {item}
                  <button onClick={() => removeItem('offering', item)} className="hover:text-white">
                    <X size={12} />
                  </button>
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
                placeholder="e.g., Fence repair"
                className="input-field flex-1 text-sm"
                data-testid="trade-requesting-input"
              />
              <button
                onClick={() => addItem('requesting')}
                className="btn-secondary px-3 flex items-center gap-1 text-sm"
                data-testid="add-requesting-btn"
              >
                <Plus size={16} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {requesting.map((item) => (
                <span key={item} className="badge badge-looking flex items-center gap-1" data-testid="requesting-tag">
                  {item}
                  <button onClick={() => removeItem('requesting', item)} className="hover:text-white">
                    <X size={12} />
                  </button>
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
              placeholder="Add details about your trade offer..."
              className="input-field w-full text-sm resize-none"
              rows={3}
              data-testid="trade-message-input"
            />
          </div>

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={submitting || offering.length === 0 || requesting.length === 0}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            data-testid="submit-trade-btn"
          >
            <PaperPlaneTilt size={18} weight="bold" />
            {submitting ? 'Sending...' : 'Send Trade Offer'}
          </button>
        </div>
      </div>
    </div>
  );
}
