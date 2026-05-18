import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Flag, Check, X as XIcon, Eye } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const REASON_LABELS = {
  spam: 'Spam',
  harassment: 'Harassment',
  hate_speech: 'Hate Speech',
  nsfw: 'NSFW',
  scam: 'Scam',
  impersonation: 'Impersonation',
  violence: 'Violence',
  other: 'Other'
};

const TARGET_LABELS = {
  user: 'User',
  post: 'Barter Post',
  community_post: 'Community Post',
  comment: 'Comment',
  gallery_item: 'Gallery Item'
};

export default function ReportsPanel({ onViewProfile }) {
  const [filter, setFilter] = useState('pending');
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState({ pending: 0, resolved: 0, dismissed: 0 });
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [list, s] = await Promise.all([
        axios.get(`${API_URL}/api/admin/reports?status=${filter}`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/reports/stats`, { withCredentials: true })
      ]);
      setReports(list.data?.reports || []);
      setStats(s.data || { pending: 0, resolved: 0, dismissed: 0 });
    } catch (err) {
      console.error('Failed to load reports', err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const updateReport = async (id, status) => {
    try {
      await axios.put(
        `${API_URL}/api/admin/reports/${id}`,
        { status, resolution_note: '' },
        { withCredentials: true }
      );
      toast.success(`Report ${status}`);
      fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update');
    }
  };

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]" data-testid="admin-reports-panel">
      <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2 flex-wrap">
        <Flag size={16} className="text-red-400" />
        <span className="text-sm font-medium text-[var(--text-primary)]">Moderation Reports</span>
        <div className="ml-auto flex items-center gap-1">
          {['pending', 'resolved', 'dismissed', 'all'].map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-2 py-1 text-[10px] font-medium uppercase border ${
                filter === s
                  ? 'bg-[var(--brand-primary)] text-white border-[var(--brand-primary)]'
                  : 'border-[var(--border-color)] text-[var(--text-muted)] hover:bg-[var(--bg-surface-hover)]'
              }`}
              data-testid={`reports-filter-${s}`}
            >
              {s}
              {s !== 'all' && stats[s] !== undefined && (
                <span className="ml-1 opacity-75">({stats[s]})</span>
              )}
            </button>
          ))}
        </div>
      </div>
      <div className="max-h-[420px] overflow-y-auto">
        {loading ? (
          <div className="py-6 text-center text-xs text-[var(--text-muted)]">Loading...</div>
        ) : reports.length === 0 ? (
          <div className="py-6 text-center text-xs text-[var(--text-muted)]">
            No {filter === 'all' ? '' : filter} reports.
          </div>
        ) : (
          reports.map(r => (
            <div
              key={r._id}
              className="p-2.5 border-b border-[var(--border-color)] text-xs hover:bg-[var(--bg-surface-hover)]"
              data-testid={`report-row-${r._id}`}
            >
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className="px-1.5 py-0.5 text-[9px] font-medium uppercase bg-red-900/30 text-red-400 rounded">
                  {REASON_LABELS[r.reason] || r.reason}
                </span>
                <span className="px-1.5 py-0.5 text-[9px] font-medium uppercase bg-[var(--bg-surface-hover)] text-[var(--text-muted)] rounded">
                  {TARGET_LABELS[r.target_type] || r.target_type}
                </span>
                <span className="text-[10px] text-[var(--text-muted)] ml-auto">
                  {new Date(r.created_at).toLocaleString()}
                </span>
              </div>
              <p className="text-[var(--text-primary)] mb-1">
                <span className="text-[var(--text-muted)]">By </span>
                <button
                  onClick={() => onViewProfile?.(r.reporter_id)}
                  className="font-medium hover:text-[var(--brand-primary)] hover:underline"
                  data-testid={`report-reporter-${r._id}`}
                >
                  {r.reporter_name}
                </button>
                <span className="text-[var(--text-muted)]"> • Target: </span>
                <code className="text-[10px] text-[var(--text-secondary)]">{r.target_id}</code>
              </p>
              {r.details && (
                <p className="text-[var(--text-secondary)] mb-1.5 line-clamp-2 italic">"{r.details}"</p>
              )}
              <div className="flex items-center gap-1.5">
                {r.target_type === 'user' && (
                  <button
                    onClick={() => onViewProfile?.(r.target_id)}
                    className="px-2 py-1 text-[10px] border border-[var(--border-color)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] flex items-center gap-1"
                    data-testid={`report-view-target-${r._id}`}
                  >
                    <Eye size={11} />
                    View User
                  </button>
                )}
                {r.status === 'pending' && (
                  <>
                    <button
                      onClick={() => updateReport(r._id, 'resolved')}
                      className="px-2 py-1 text-[10px] font-medium bg-green-700 hover:bg-green-800 text-white flex items-center gap-1"
                      data-testid={`report-resolve-${r._id}`}
                    >
                      <Check size={11} />
                      Resolve
                    </button>
                    <button
                      onClick={() => updateReport(r._id, 'dismissed')}
                      className="px-2 py-1 text-[10px] font-medium bg-gray-600 hover:bg-gray-700 text-white flex items-center gap-1"
                      data-testid={`report-dismiss-${r._id}`}
                    >
                      <XIcon size={11} />
                      Dismiss
                    </button>
                  </>
                )}
                {r.status !== 'pending' && (
                  <span
                    className={`px-2 py-1 text-[10px] font-medium uppercase rounded ${
                      r.status === 'resolved'
                        ? 'bg-green-900/30 text-green-400'
                        : 'bg-gray-700/30 text-gray-400'
                    }`}
                  >
                    {r.status}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
