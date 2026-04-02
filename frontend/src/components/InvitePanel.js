import { useState, useEffect } from 'react';
import axios from 'axios';
import { LinkSimple, Copy, Check, PaperPlaneTilt, Clock, UserPlus } from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InvitePanel() {
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [copiedToken, setCopiedToken] = useState(null);

  useEffect(() => {
    fetchInvites();
  }, []);

  const fetchInvites = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/invites/my-invites`, { withCredentials: true });
      setInvites(res.data);
    } catch (err) {
      console.error('Error fetching invites:', err);
    } finally {
      setLoading(false);
    }
  };

  const createInvite = async () => {
    setCreating(true);
    try {
      const res = await axios.post(`${API_URL}/api/invites/create`, {}, { withCredentials: true });
      const newToken = res.data.token;
      await fetchInvites();
      copyToClipboard(newToken);
    } catch (err) {
      console.error('Error creating invite:', err);
    } finally {
      setCreating(false);
    }
  };

  const copyToClipboard = (token) => {
    const link = `${window.location.origin}/register?invite=${token}`;
    navigator.clipboard.writeText(link).then(() => {
      setCopiedToken(token);
      setTimeout(() => setCopiedToken(null), 2500);
    });
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const isExpired = (dateStr) => {
    const created = new Date(dateStr);
    const now = new Date();
    return (now - created) > 7 * 24 * 60 * 60 * 1000;
  };

  return (
    <div className="max-w-2xl mx-auto p-4 sm:p-6" data-testid="invite-panel">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-[var(--text-primary)] flex items-center gap-2">
            <UserPlus size={24} weight="duotone" className="text-[var(--brand-primary)]" />
            Invite to Network
          </h2>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            Generate invite links to bring trusted people into the network.
          </p>
        </div>
      </div>

      <button
        onClick={createInvite}
        disabled={creating}
        className="btn-primary flex items-center gap-2 mb-6"
        data-testid="create-invite-button"
      >
        <PaperPlaneTilt size={18} weight="bold" />
        {creating ? 'Generating...' : 'Generate Invite Link'}
      </button>

      <div className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-muted)]">
          Your Invites ({invites.length})
        </h3>

        {loading ? (
          <p className="text-[var(--text-muted)] text-sm">Loading invites...</p>
        ) : invites.length === 0 ? (
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-6 text-center">
            <LinkSimple size={32} className="text-[var(--text-muted)] mx-auto mb-2" />
            <p className="text-[var(--text-muted)] text-sm">No invites yet. Generate one to invite someone to the network.</p>
          </div>
        ) : (
          invites.map((inv) => {
            const expired = !inv.used && isExpired(inv.created_at);
            return (
              <div
                key={inv.token}
                className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 flex flex-col sm:flex-row sm:items-center gap-3"
                data-testid={`invite-item-${inv.token.slice(0, 8)}`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {inv.used ? (
                      <span className="text-xs px-2 py-0.5 bg-green-900/30 text-green-400 border border-green-800/50 rounded-sm font-medium">
                        USED
                      </span>
                    ) : expired ? (
                      <span className="text-xs px-2 py-0.5 bg-red-900/30 text-red-400 border border-red-800/50 rounded-sm font-medium">
                        EXPIRED
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 bg-[var(--brand-primary)]/20 text-[var(--brand-primary)] border border-[var(--brand-primary)]/30 rounded-sm font-medium">
                        ACTIVE
                      </span>
                    )}
                    {inv.used_by_name && (
                      <span className="text-sm text-[var(--text-secondary)]">
                        Joined: <span className="font-medium text-[var(--text-primary)]">{inv.used_by_name}</span>
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
                    <Clock size={12} />
                    <span>Created {formatDate(inv.created_at)}</span>
                    {!inv.used && !expired && <span className="text-[var(--text-muted)]">· Expires in 7 days</span>}
                  </div>
                </div>

                {!inv.used && !expired && (
                  <button
                    onClick={() => copyToClipboard(inv.token)}
                    className="flex items-center gap-1.5 text-sm px-3 py-1.5 border border-[var(--border-color)] hover:border-[var(--brand-primary)] text-[var(--text-secondary)] hover:text-[var(--brand-primary)] transition-colors"
                    data-testid={`copy-invite-${inv.token.slice(0, 8)}`}
                  >
                    {copiedToken === inv.token ? (
                      <>
                        <Check size={14} weight="bold" className="text-green-400" />
                        <span className="text-green-400">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy size={14} />
                        Copy Link
                      </>
                    )}
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
