import {
  DotsThree,
  User,
  ArrowsLeftRight,
  ChatText,
  Warning,
  PencilSimple,
  Trash,
  ShieldSlash
} from '@phosphor-icons/react';

export default function PostMenu({
  postId,
  isOpen,
  setOpen,
  isOwner,
  isAdmin,
  isOtherUser,
  onViewProfile,
  onProposeTrade,
  onStartChat,
  onEdit,
  onDelete,
  onReport,
  onBlock
}) {
  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!isOpen)}
        className="btn-ghost p-1.5 md:p-2 flex-shrink-0 hover:bg-[var(--bg-surface-hover)]"
        data-testid={`post-menu-btn-${postId}`}
      >
        <DotsThree size={18} weight="bold" />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div
            className="absolute right-0 mt-1 w-48 bg-[var(--bg-surface)] border border-[var(--border-color)] rounded-lg shadow-xl z-50 overflow-hidden"
            data-testid={`post-menu-dropdown-${postId}`}
          >
            <button
              onClick={onViewProfile}
              className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
              data-testid={`post-menu-view-profile-${postId}`}
            >
              <User size={16} />
              View Profile
            </button>
            {isOtherUser && (
              <>
                <button
                  onClick={onProposeTrade}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                  data-testid={`post-menu-trade-${postId}`}
                >
                  <ArrowsLeftRight size={16} />
                  Propose Trade
                </button>
                <button
                  onClick={onStartChat}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                  data-testid={`post-menu-message-${postId}`}
                >
                  <ChatText size={16} />
                  Send Message
                </button>
                {onReport && (
                  <button
                    onClick={onReport}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--brand-danger)] hover:bg-[var(--bg-surface-hover)] transition-colors border-t border-[var(--border-color)]"
                    data-testid={`post-menu-report-${postId}`}
                  >
                    <Warning size={16} />
                    Report Post
                  </button>
                )}
                {onBlock && (
                  <button
                    onClick={onBlock}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--brand-danger)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                    data-testid={`post-menu-block-${postId}`}
                  >
                    <ShieldSlash size={16} />
                    Block User
                  </button>
                )}
              </>
            )}
            {isOwner && onEdit && (
              <button
                onClick={onEdit}
                className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors border-t border-[var(--border-color)]"
                data-testid={`post-menu-edit-${postId}`}
              >
                <PencilSimple size={16} />
                Edit Post
              </button>
            )}
            {(isOwner || isAdmin) && onDelete && (
              <button
                onClick={onDelete}
                className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--brand-danger)] hover:bg-[var(--bg-surface-hover)] transition-colors border-t border-[var(--border-color)]"
                data-testid={`post-menu-delete-${postId}`}
              >
                <Trash size={16} />
                Delete Post
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
