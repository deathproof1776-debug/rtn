import { useState } from 'react';
import { SealCheck, Crown, CaretDown, Eye, Trash, ShieldStar } from '@phosphor-icons/react';

export default function QuickUserRow({ user, onVerify, onChangeRole, onDelete, onViewProfile, currentUserId }) {
  const [showActions, setShowActions] = useState(false);
  const isSelf = user._id === currentUserId;

  return (
    <div className="flex items-center gap-2 p-2 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] text-xs">
      <div className="w-7 h-7 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] text-xs font-bold flex-shrink-0">
        {user.name?.charAt(0)?.toUpperCase() || 'U'}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span className="font-medium text-[var(--text-primary)] truncate">{user.name}</span>
          {user.is_verified && <SealCheck size={12} className="text-[var(--brand-primary)]" weight="fill" />}
          {user.role === 'admin' && <Crown size={12} className="text-[var(--brand-accent)]" />}
          {user.role === 'moderator' && <ShieldStar size={12} className="text-[#0369A1]" weight="fill" />}
        </div>
        <p className="text-[10px] text-[var(--text-muted)] truncate">{user.email}</p>
      </div>
      <div className="relative flex-shrink-0">
        <button
          onClick={() => setShowActions(!showActions)}
          className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
          data-testid={`user-actions-${user._id}`}
        >
          <CaretDown size={14} />
        </button>
        {showActions && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setShowActions(false)} />
            <div className="absolute right-0 top-full mt-1 z-50 bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-lg min-w-[150px]">
              <button
                onClick={() => { onViewProfile?.(user._id); setShowActions(false); }}
                className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
              >
                <Eye size={14} /> View Profile
              </button>
              <button
                onClick={() => { onVerify(user._id, !user.is_verified); setShowActions(false); }}
                className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
              >
                <SealCheck size={14} /> {user.is_verified ? 'Unverify' : 'Verify'}
              </button>
              {!isSelf && (
                <>
                  {user.role !== 'admin' && (
                    <button
                      onClick={() => { onChangeRole(user._id, user.role === 'moderator' ? 'user' : 'moderator'); setShowActions(false); }}
                      disabled={!user.is_verified && user.role !== 'moderator'}
                      title={(!user.is_verified && user.role !== 'moderator') ? 'Only verified traders can be moderators' : ''}
                      className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)] disabled:opacity-40 disabled:cursor-not-allowed"
                      data-testid={`toggle-moderator-${user._id}`}
                    >
                      <ShieldStar size={14} /> {user.role === 'moderator' ? 'Remove Moderator' : 'Make Moderator'}
                    </button>
                  )}
                  <button
                    onClick={() => { onChangeRole(user._id, user.role === 'admin' ? 'user' : 'admin'); setShowActions(false); }}
                    className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
                  >
                    <Crown size={14} /> {user.role === 'admin' ? 'Demote' : 'Promote to Admin'}
                  </button>
                  <button
                    onClick={() => { onDelete(user._id, user.name); setShowActions(false); }}
                    className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-red-400"
                  >
                    <Trash size={14} /> Delete
                  </button>
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
