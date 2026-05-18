import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { UserMinus, ShieldSlash } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function BlockedUsersPanel() {
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchBlocks = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/api/moderation/blocks`, { withCredentials: true });
      setBlocks(res.data?.blocks || []);
    } catch {
      setBlocks([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchBlocks(); }, [fetchBlocks]);

  const handleUnblock = async (userId) => {
    try {
      await axios.delete(`${API_URL}/api/moderation/block/${userId}`, { withCredentials: true });
      setBlocks(blocks.filter(b => b.user_id !== userId));
      toast.success('User unblocked');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to unblock');
    }
  };

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]" data-testid="blocked-users-panel">
      <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
        <ShieldSlash size={16} className="text-red-400" />
        <span className="text-sm font-medium text-[var(--text-primary)]">Blocked Users</span>
        <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] ml-auto">
          {blocks.length}
        </span>
      </div>
      <div className="max-h-[260px] overflow-y-auto">
        {loading ? (
          <div className="py-6 text-center text-xs text-[var(--text-muted)]">Loading...</div>
        ) : blocks.length === 0 ? (
          <div className="py-6 text-center text-xs text-[var(--text-muted)]">
            No blocked users. Use the post menu or profile to block users.
          </div>
        ) : (
          blocks.map(b => (
            <div
              key={b.user_id}
              className="flex items-center gap-2 p-2 border-b border-[var(--border-color)] text-xs"
              data-testid={`blocked-row-${b.user_id}`}
            >
              <div className="w-7 h-7 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] text-xs font-bold flex-shrink-0">
                {b.name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-[var(--text-primary)] truncate">{b.name}</p>
                <p className="text-[10px] text-[var(--text-muted)]">
                  Blocked {new Date(b.blocked_at).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={() => handleUnblock(b.user_id)}
                className="px-2 py-1 text-[10px] font-medium border border-[var(--border-color)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] flex items-center gap-1"
                data-testid={`unblock-btn-${b.user_id}`}
              >
                <UserMinus size={12} />
                Unblock
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
