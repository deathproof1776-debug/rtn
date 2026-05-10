import { Article, Trash } from '@phosphor-icons/react';

export default function PostsPanel({ posts, onDelete }) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
      <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
        <Article size={16} className="text-blue-500" />
        <span className="text-sm font-medium text-[var(--text-primary)]">Barter Posts</span>
        <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] ml-auto">
          {posts.length}
        </span>
      </div>
      <div className="max-h-[250px] overflow-y-auto">
        {posts.slice(0, 10).map(p => (
          <div
            key={p._id}
            className="flex items-start gap-2 p-2 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] text-xs"
          >
            <div className="flex-1 min-w-0">
              <span className="font-medium text-[var(--text-primary)] line-clamp-1">{p.title}</span>
              <p className="text-[10px] text-[var(--text-muted)]">by {p.user_name}</p>
            </div>
            <button
              onClick={() => onDelete(p._id, `post "${p.title}"`, 'post')}
              className="p-1 text-[var(--text-muted)] hover:text-red-400"
            >
              <Trash size={14} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
