import { ShieldCheck, ArrowLeft } from '@phosphor-icons/react';
import ReportsPanel from '../components/admin/ReportsPanel';

export default function ModerationDashboard({ onBack, onViewProfile }) {
  return (
    <div className="max-w-3xl mx-auto" data-testid="moderation-dashboard">
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={onBack}
          className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)]"
          data-testid="moderation-back-button"
        >
          <ArrowLeft size={20} />
        </button>
        <ShieldCheck size={24} weight="duotone" className="text-[var(--brand-primary)]" />
        <h2 className="text-xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Moderation Queue
        </h2>
      </div>
      <p className="text-xs text-[var(--text-muted)] mb-3">
        Review community reports. Resolve, dismiss, or escalate to an admin. You can also remove flagged posts and comments directly from the feed.
      </p>
      <ReportsPanel onViewProfile={onViewProfile} />
    </div>
  );
}
