import { useState } from 'react';
import axios from 'axios';
import { X, Warning } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const REASONS = [
  { id: 'spam', label: 'Spam or misleading' },
  { id: 'harassment', label: 'Harassment or bullying' },
  { id: 'hate_speech', label: 'Hate speech' },
  { id: 'nsfw', label: 'NSFW / Sexual content' },
  { id: 'scam', label: 'Scam or fraud' },
  { id: 'impersonation', label: 'Impersonation' },
  { id: 'violence', label: 'Violence or threats' },
  { id: 'other', label: 'Other' }
];

const TARGET_LABELS = {
  user: 'this user',
  post: 'this barter post',
  community_post: 'this community post',
  comment: 'this comment',
  gallery_item: 'this gallery item'
};

export default function ReportModal({ targetType, targetId, onClose }) {
  const [reason, setReason] = useState('');
  const [details, setDetails] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason) return;
    setSubmitting(true);
    try {
      const res = await axios.post(
        `${API_URL}/api/moderation/report`,
        { target_type: targetType, target_id: targetId, reason, details },
        { withCredentials: true }
      );
      toast.success(res.data?.message || 'Report submitted');
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit report');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/70"
      onClick={onClose}
      data-testid="report-modal"
    >
      <div
        className="bg-[var(--bg-surface)] border border-[var(--border-color)] max-w-md w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-4 py-3 border-b border-[var(--border-color)] flex items-center gap-2">
          <Warning size={18} className="text-red-400" />
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            Report {TARGET_LABELS[targetType] || 'this content'}
          </h3>
          <button onClick={onClose} className="ml-auto p-1 hover:bg-[var(--bg-surface-hover)] rounded">
            <X size={18} className="text-[var(--text-muted)]" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <p className="text-xs text-[var(--text-muted)]">
            Reports go to the moderation team. Anonymous to the reported party.
          </p>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
              Reason
            </label>
            <div className="space-y-1.5">
              {REASONS.map(r => (
                <label
                  key={r.id}
                  className="flex items-center gap-2 p-2 border border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] cursor-pointer text-xs"
                  data-testid={`report-reason-${r.id}`}
                >
                  <input
                    type="radio"
                    name="reason"
                    value={r.id}
                    checked={reason === r.id}
                    onChange={() => setReason(r.id)}
                    className="w-3 h-3"
                  />
                  <span className="text-[var(--text-primary)]">{r.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
              Additional context (optional)
            </label>
            <textarea
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              maxLength={1000}
              rows={3}
              className="input-field w-full text-sm resize-none"
              placeholder="Describe what's wrong (max 1000 chars)..."
              data-testid="report-details-input"
            />
          </div>

          <div className="flex gap-2 justify-end pt-1">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary px-3 py-1.5 text-xs"
              data-testid="report-cancel-btn"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!reason || submitting}
              className="px-3 py-1.5 text-xs font-medium bg-red-600 hover:bg-red-700 text-white disabled:opacity-50"
              data-testid="report-submit-btn"
            >
              {submitting ? 'Submitting...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
