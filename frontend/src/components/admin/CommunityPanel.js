import { UsersThree } from '@phosphor-icons/react';
import CommunityPostRow from './CommunityPostRow';

export default function CommunityPanel({ communityPosts, onDelete }) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
      <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
        <UsersThree size={16} className="text-purple-500" />
        <span className="text-sm font-medium text-[var(--text-primary)]">Community Feed</span>
        <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] ml-auto">
          {communityPosts.length}
        </span>
      </div>
      <div className="max-h-[250px] overflow-y-auto">
        {communityPosts.length === 0 ? (
          <div className="py-6 text-center text-xs text-[var(--text-muted)]">No community posts</div>
        ) : (
          communityPosts
            .slice(0, 10)
            .map(p => (
              <CommunityPostRow
                key={p._id}
                post={p}
                onDelete={(id, label) => onDelete(id, label, 'community')}
              />
            ))
        )}
      </div>
    </div>
  );
}
