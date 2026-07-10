import { useState, useRef } from 'react';
import { SealCheck, Crown, CaretDown, Eye, Trash, ShieldStar, Prohibit } from '@phosphor-icons/react';

export default function QuickUserRow({ user, onVerify, onChangeRole, onDelete, onBan, onViewProfile, currentUserId }) {
  const [showActions, setShowActions] = useState(false);
  const [menuStyle, setMenuStyle] = useState({});
  const btnRef = useRef(null);
  const isSelf = user._id === currentUserId;

  const openMenu = () => {
    if (btnRef.current) {
      const rect = btnRef.current.getBoundingClientRect();
      setMenuStyle({
        position: 'fixed',
        top: rect.bottom + 4,
        right: window.innerWidth - rect.right,
        zIndex: 9999,
        minWidth: '160px',
      });
    }
    setShowActions(true);
  };

  const closeMenu = () => setShowActions(false);

  return (
    <div className={`flex items-center gap-2 p-2 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] text-xs ${user.banned ? 'opacity-60' : ''}`}>
      <div className="w-7 h-7 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] text-xs font-bold flex-shrink-0 overflow-hidden">
        {user.avatar ? (
          <img src={user.avatar} alt="" className="w-full h-full object-cover" />
        ) : (
          user.name?.charAt(0)?.toUpperCase() || 'U'
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1 flex-wrap">
          <span className="font-medium text-[var(--text-primary)] truncate">{user.name}</span>
          {user.is_verified && <SealCheck size={12} className="text-[var(--brand-primary)] flex-shrink-0" weight="fill" />}
          {user.role === 'admin' && <Crown size={12} className="text-[var(--brand-accent)] flex-shrink-0" />}
          {user.role === 'moderator' && <ShieldStar size={12} className="text-[#0369A1] flex-shrink-0" weight="fill" />}
          {user.banned && <span className="text-[9px] px-1 py-0.5 bg-red-900/40 text-red-400 rounded">Banned</span>}
        </div>
        <p className="text-[10px] text-[var(--text-muted)] truncate">{user.email}</p>
      </div>
      <div className="relative flex-shrink-0">
        <button
          ref={btnRef}
          onClick={showActions ? closeMenu : openMenu}
          className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
          data-testid={`user-actions-${user._id}`}
        >
          <CaretDown size={14} />
        </button>
        {showActions && (
          <>
            <div className="fixed inset-0 z-[9998]" onClick={closeMenu} />
            <div
              style={menuStyle}
              className="bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-xl"
            >
              <button
                onClick={() => { onViewProfile?.(user._id); closeMenu(); }}
                className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
              >
                <Eye size={14} /> View Profile
              </button>
              <button
                onClick={() => { onVerify(user._id, !user.is_verified); closeMenu(); }}
                className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
              >
                <SealCheck size={14} /> {user.is_verified ? 'Unverify' : 'Verify'}
              </button>
              {!isSelf && (
                <>
                  {user.role !== 'admin' && (
                    <button
                      onClick={() => { onChangeRole(user._id, user.role === 'moderator' ? 'user' : 'moderator'); closeMenu(); }}
                      disabled={!user.is_verified && user.role !== 'moderator'}
                      title={(!user.is_verified && user.role !== 'moderator') ? 'Only verified traders can be moderators' : ''}
                      className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)] disabled:opacity-40 disabled:cursor-not-allowed"
                      data-testid={`toggle-moderator-${user._id}`}
                    >
                      <ShieldStar size={14} /> {user.role === 'moderator' ? 'Remove Moderator' : 'Make Moderator'}
                    </button>
                  )}
                  <button
                    onClick={() => { onChangeRole(user._id, user.role === 'admin' ? 'user' : 'admin'); closeMenu(); }}
                    className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
                  >
                    <Crown size={14} /> {user.role === 'admin' ? 'Demote' : 'Promote to Admin'}
                  </button>
                  <button
                    onClick={() => { onBan?.(user._id); closeMenu(); }}
                    className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-amber-400"
                    data-testid={`ban-user-${user._id}`}
                  >
                    <Prohibit size={14} /> {user.banned ? 'Unban User' : 'Ban User'}
                  </button>
                  <button
                    onClick={() => { onDelete(user._id, user.name); closeMenu(); }}
                    className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-red-400 border-t border-[var(--border-color)]"
                    data-testid={`delete-user-${user._id}`}
                  >
                    <Trash size={14} /> Delete User
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
