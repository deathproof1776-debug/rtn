import { Users, MagnifyingGlass } from '@phosphor-icons/react';
import QuickUserRow from './QuickUserRow';

export default function UsersPanel({
  users,
  filteredUsers,
  searchQuery,
  setSearchQuery,
  currentUserId,
  onVerify,
  onChangeRole,
  onDelete,
  onBan,
  onViewProfile
}) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
      <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
        <Users size={16} className="text-[var(--brand-primary)]" />
        <span className="text-sm font-medium text-[var(--text-primary)]">Users</span>
        <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] ml-auto">
          {users.length}
        </span>
      </div>
      <div className="p-2 border-b border-[var(--border-color)]">
        <div className="relative">
          <MagnifyingGlass size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field w-full text-xs py-1.5 pl-7"
            placeholder="Search users..."
          />
        </div>
      </div>
      {/* No overflow constraint — page scrolls naturally so dropdowns are never clipped */}
      <div>
        {filteredUsers.slice(0, 50).map(u => (
          <QuickUserRow
            key={u._id}
            user={u}
            currentUserId={currentUserId}
            onVerify={onVerify}
            onChangeRole={onChangeRole}
            onDelete={(id, name) => onDelete(id, `user "${name}"`, 'user')}
            onBan={onBan}
            onViewProfile={onViewProfile}
          />
        ))}
      </div>
    </div>
  );
}
