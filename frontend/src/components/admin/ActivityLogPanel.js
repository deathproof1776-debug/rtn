import { ClockCounterClockwise, SealCheck, Crown, Trash, UserMinus, Notepad } from '@phosphor-icons/react';

const getTimeAgo = (dateStr) => {
  const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

const ACTION_ICONS = {
  verified: { icon: SealCheck, color: 'var(--brand-accent)' },
  unverified: { icon: SealCheck, color: '#DC2626' },
  role_changed: { icon: Crown, color: 'var(--brand-primary)' },
  deleted_post: { icon: Trash, color: '#DC2626' },
  deleted_user: { icon: UserMinus, color: '#DC2626' }
};

export default function ActivityLogPanel({ auditLogs }) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
      <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
        <ClockCounterClockwise size={16} className="text-[var(--text-muted)]" />
        <span className="text-sm font-medium text-[var(--text-primary)]">Activity Log</span>
      </div>
      <div className="max-h-[520px] overflow-y-auto">
        {auditLogs.length === 0 ? (
          <div className="py-8 text-center text-xs text-[var(--text-muted)]">No activity yet</div>
        ) : (
          auditLogs.map((log, idx) => {
            const config = ACTION_ICONS[log.action] || { icon: Notepad, color: 'var(--text-muted)' };
            const ActionIcon = config.icon;

            return (
              <div key={log._id || idx} className="flex items-start gap-2 px-3 py-2 border-b border-[var(--border-color)] text-xs">
                <div
                  className="w-6 h-6 flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: `${config.color}20` }}
                >
                  <ActionIcon size={12} style={{ color: config.color }} weight="fill" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[var(--text-primary)]">
                    <span className="font-medium">{log.admin_name}</span>
                    <span className="text-[var(--text-muted)]"> → </span>
                    <span className="font-medium">{log.target_name}</span>
                  </p>
                  <p className="text-[10px] text-[var(--text-muted)]">{log.action.replace('_', ' ')} • {getTimeAgo(log.created_at)}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
