import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { 
  ChatCircle, 
  ArrowBendDownRight,
  PaperPlaneTilt,
  CaretDown,
  CaretUp,
  Trash
} from '@phosphor-icons/react';

/**
 * ThreadedComments - Reusable comment component with reply threading
 * 
 * Props:
 * - comments: Array of comment objects with { id, user_id, user_name, content, parent_id, replies, created_at }
 * - onAddComment: Function(content, parentId) - Called when adding a new comment or reply
 * - onDeleteComment: Function(commentId) - Called when deleting a comment (optional)
 * - currentUserId: String - Current logged in user's ID
 * - maxDepth: Number - Maximum nesting depth (default: 2)
 */
export default function ThreadedComments({ 
  comments = [], 
  onAddComment, 
  onDeleteComment,
  currentUserId,
  maxDepth = 2
}) {
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyContent, setReplyContent] = useState('');
  const [expandedThreads, setExpandedThreads] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Build a map of comments by ID for quick lookup
  const commentMap = {};
  comments.forEach(c => {
    commentMap[c.id] = c;
  });

  // Get top-level comments (no parent_id)
  const topLevelComments = comments.filter(c => !c.parent_id);

  // Get replies for a comment
  const getReplies = (commentId) => {
    return comments.filter(c => c.parent_id === commentId);
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim() || submitting) return;
    
    setSubmitting(true);
    try {
      await onAddComment(newComment.trim(), null);
      setNewComment('');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitReply = async (parentId) => {
    if (!replyContent.trim() || submitting) return;
    
    setSubmitting(true);
    try {
      await onAddComment(replyContent.trim(), parentId);
      setReplyContent('');
      setReplyingTo(null);
    } finally {
      setSubmitting(false);
    }
  };

  const toggleThread = (commentId) => {
    setExpandedThreads(prev => ({
      ...prev,
      [commentId]: !prev[commentId]
    }));
  };

  // Render a single comment
  const renderComment = (comment, depth = 0) => {
    const replies = getReplies(comment.id);
    const hasReplies = replies.length > 0;
    const isExpanded = expandedThreads[comment.id] !== false; // Default expanded
    const canReply = depth < maxDepth;
    const isOwn = comment.user_id === currentUserId;

    return (
      <div 
        key={comment.id} 
        className={`${depth > 0 ? 'ml-4 pl-3 border-l-2 border-[var(--border-color)]' : ''}`}
        data-testid={`comment-${comment.id}`}
      >
        <div className="py-2">
          {/* Comment header */}
          <div className="flex items-start gap-2">
            <div className="w-7 h-7 rounded-full bg-[var(--brand-primary)] flex items-center justify-center text-white font-bold text-xs shrink-0">
              {comment.user_name?.[0]?.toUpperCase() || '?'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm text-[var(--text-primary)]">
                  {comment.user_name}
                </span>
                <span className="text-xs text-[var(--text-muted)]">
                  {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
                </span>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mt-0.5 break-words">
                {comment.content}
              </p>
              
              {/* Comment actions */}
              <div className="flex items-center gap-3 mt-1">
                {canReply && (
                  <button
                    onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
                    className="text-xs text-[var(--text-muted)] hover:text-[var(--brand-primary)] flex items-center gap-1"
                    data-testid={`reply-btn-${comment.id}`}
                  >
                    <ArrowBendDownRight size={12} />
                    Reply
                  </button>
                )}
                {hasReplies && (
                  <button
                    onClick={() => toggleThread(comment.id)}
                    className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] flex items-center gap-1"
                  >
                    {isExpanded ? <CaretUp size={12} /> : <CaretDown size={12} />}
                    {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
                  </button>
                )}
                {isOwn && onDeleteComment && (
                  <button
                    onClick={() => onDeleteComment(comment.id)}
                    className="text-xs text-[var(--text-muted)] hover:text-red-500 flex items-center gap-1"
                    data-testid={`delete-comment-${comment.id}`}
                  >
                    <Trash size={12} />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Reply input */}
          {replyingTo === comment.id && (
            <div className="mt-2 ml-9 flex items-center gap-2">
              <input
                type="text"
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder={`Reply to ${comment.user_name}...`}
                className="flex-1 px-3 py-1.5 text-sm bg-[var(--bg-main)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmitReply(comment.id);
                  }
                }}
                autoFocus
                data-testid={`reply-input-${comment.id}`}
              />
              <button
                onClick={() => handleSubmitReply(comment.id)}
                disabled={!replyContent.trim() || submitting}
                className="p-1.5 text-[var(--brand-primary)] disabled:opacity-50"
                data-testid={`reply-submit-${comment.id}`}
              >
                <PaperPlaneTilt size={18} />
              </button>
            </div>
          )}
        </div>

        {/* Nested replies */}
        {hasReplies && isExpanded && (
          <div className="mt-1">
            {replies.map(reply => renderComment(reply, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-1" data-testid="threaded-comments">
      {/* New comment input */}
      <form onSubmit={handleSubmitComment} className="flex items-center gap-2 mb-3">
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
          className="flex-1 px-3 py-2 text-sm bg-[var(--bg-main)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
          data-testid="new-comment-input"
        />
        <button
          type="submit"
          disabled={!newComment.trim() || submitting}
          className="p-2 text-[var(--brand-primary)] disabled:opacity-50"
          data-testid="new-comment-submit"
        >
          <PaperPlaneTilt size={20} />
        </button>
      </form>

      {/* Comments list */}
      {topLevelComments.length === 0 ? (
        <p className="text-sm text-[var(--text-muted)] text-center py-4">
          No comments yet. Be the first to comment!
        </p>
      ) : (
        <div className="space-y-1">
          {topLevelComments.map(comment => renderComment(comment))}
        </div>
      )}
    </div>
  );
}
