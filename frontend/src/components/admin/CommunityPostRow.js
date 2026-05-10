import { Trash } from '@phosphor-icons/react';

export default function CommunityPostRow({ post, onDelete }) {
  return (
    <div className="flex items-start gap-2 p-2 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] text-xs">
      <div className="w-6 h-6 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] text-[10px] font-bold flex-shrink-0">
        {post.user_name?.charAt(0)?.toUpperCase() || 'U'}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1 flex-wrap">
          <span className="font-medium text-[var(--text-primary)]">{post.user_name}</span>
          {post.category && <span className="text-[9px] px-1 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)]">{post.category}</span>}
        </div>
        <p className="text-[var(--text-secondary)] line-clamp-1">{post.content || post.title}</p>
        <p className="text-[9px] text-[var(--text-muted)] mt-0.5">{new Date(post.created_at).toLocaleDateString()}</p>
      </div>
      <button
        onClick={() => onDelete(post._id, 'this community post')}
        className="p-1 text-[var(--text-muted)] hover:text-red-400 flex-shrink-0"
      >
        <Trash size={14} />
      </button>
    </div>
  );
}
