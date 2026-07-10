import { useState } from 'react';
import axios from 'axios';
import { Megaphone, X } from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ChangelogModal({ changelog, onDismiss }) {
  const [dismissing, setDismissing] = useState(false);

  if (!changelog) return null;

  const dismiss = async () => {
    setDismissing(true);
    try {
      await axios.post(`${API_URL}/api/changelog/${changelog._id}/ack`, {}, { withCredentials: true });
    } catch (_) { /* non-blocking */ }
    onDismiss?.();
  };

  const SECTION_ICONS = {
    photos: '📸',
    content: '🔗',
    security: '🔐',
    identity: '🪪',
    admin: '🛡️',
    general: '✦',
  };

  return (
    <div
      className="fixed inset-0 z-[120] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      data-testid="changelog-modal"
    >
      <div className="relative w-full max-w-md max-h-[88vh] flex flex-col bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex-shrink-0 px-5 pt-5 pb-4 border-b border-[var(--border-color)]">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[var(--brand-primary)]/20 flex items-center justify-center flex-shrink-0">
                <Megaphone size={22} weight="fill" className="text-[var(--brand-primary)]" />
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-[var(--brand-primary)] mb-0.5">
                  Platform Update · {changelog.version}
                </p>
                <h2
                  className="text-lg font-bold text-[var(--text-primary)] leading-tight"
                  style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}
                  data-testid="changelog-title"
                >
                  {changelog.title}
                </h2>
                {changelog.subtitle && (
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">{changelog.subtitle}</p>
                )}
              </div>
            </div>
            <button
              onClick={dismiss}
              disabled={dismissing}
              className="flex-shrink-0 p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors mt-0.5"
              aria-label="Dismiss"
              data-testid="changelog-dismiss-x"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Scrollable sections */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {(changelog.sections || []).map((section, si) => (
            <div key={si}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm">{SECTION_ICONS[section.icon] || '✦'}</span>
                <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">
                  {section.heading}
                </h3>
              </div>
              <div className="space-y-1.5 pl-5">
                {(section.items || []).map((item, ii) => (
                  <div key={ii} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                    <span className="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-[var(--brand-primary)] opacity-70" />
                    <span className="leading-relaxed">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 px-5 pb-5 pt-3 border-t border-[var(--border-color)]">
          <button
            onClick={dismiss}
            disabled={dismissing}
            className="btn-primary w-full py-2.5 text-sm font-medium disabled:opacity-60"
            data-testid="changelog-dismiss-btn"
          >
            {dismissing ? 'Saving...' : "Got it — Let's Trade"}
          </button>
        </div>
      </div>
    </div>
  );
}
