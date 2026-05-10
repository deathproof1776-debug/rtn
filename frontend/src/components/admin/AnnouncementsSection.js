import { Megaphone, Plus, PencilSimple } from '@phosphor-icons/react';

const TYPE_BADGES = {
  urgent: 'bg-red-900/30 text-red-400',
  warning: 'bg-yellow-900/30 text-yellow-400',
  success: 'bg-green-900/30 text-green-400',
  info: 'bg-blue-900/30 text-blue-400'
};

export default function AnnouncementsSection({ messages, onNew, onEdit }) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] mb-4">
      <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
        <Megaphone size={16} className="text-[var(--brand-accent)]" />
        <span className="text-sm font-medium text-[var(--text-primary)]">Announcements</span>
        <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)]">{messages.length}</span>
        <button onClick={onNew} className="ml-auto btn-primary px-3 py-1 text-xs flex items-center gap-1">
          <Plus size={12} weight="bold" />
          New
        </button>
      </div>
      <div className="max-h-[120px] overflow-y-auto">
        {messages.length === 0 ? (
          <div className="py-4 text-center text-xs text-[var(--text-muted)]">
            No announcements. Create one to broadcast to all users.
          </div>
        ) : (
          <div className="divide-y divide-[var(--border-color)]">
            {messages.map(msg => (
              <div key={msg._id} className="flex items-center gap-3 px-3 py-2 hover:bg-[var(--bg-surface-hover)] text-xs">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${msg.is_active ? 'bg-green-500' : 'bg-gray-500'}`} />
                <span className={`px-1.5 py-0.5 text-[9px] font-medium uppercase rounded ${TYPE_BADGES[msg.type] || TYPE_BADGES.info}`}>
                  {msg.type}
                </span>
                <span className="flex-1 text-[var(--text-primary)] truncate">{msg.message}</span>
                <span className="text-[var(--text-muted)] flex-shrink-0">Priority: {msg.priority}</span>
                <button
                  onClick={() => onEdit(msg)}
                  className="p-1 text-[var(--text-muted)] hover:text-[var(--brand-primary)] flex-shrink-0"
                >
                  <PencilSimple size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
