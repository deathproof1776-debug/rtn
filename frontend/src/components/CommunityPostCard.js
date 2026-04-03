/**
 * CommunityPostCard - Individual community post display
 */
import { useState } from 'react';
import axios from 'axios';
import { 
  Heart, 
  ChatCircle, 
  DotsThree,
  MapPin,
  CaretDown,
  CaretUp,
  SealCheck,
  Handshake,
  User,
  Trash,
  Share
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';
import ThreadedComments from './ThreadedComments';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Topic icons mapping
const TOPIC_ICONS = {
  homesteading: '🏡',
  'off-grid': '⚡',
  prepping: '🛡️',
  diy: '🔨',
  gardening: '🌱',
  livestock: '🐄',
  food: '🫙',
  energy: '☀️',
  water: '💧',
  security: '🔒',
  health: '❤️',
  finance: '💰',
  community: '👥',
  news: '📰',
  general: '💬'
};

export default function CommunityPostCard({ 
  post, 
  onLike, 
  currentUserId, 
  onViewProfile,
  onDelete,
  isAdmin = false
}) {
  const [liked, setLiked] = useState(post.likes?.includes(currentUserId));
  const [likeCount, setLikeCount] = useState(post.likes?.length || 0);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState(post.comments || []);
  const [loadingComments, setLoadingComments] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const isLongPost = post.content && post.content.length > 300;
  const isOwner = post.user_id === currentUserId;

  const handleLikeClick = async () => {
    await onLike(post._id);
    setLiked(!liked);
    setLikeCount(liked ? likeCount - 1 : likeCount + 1);
  };

  const toggleComments = () => {
    setShowComments(!showComments);
  };

  const handleAddComment = async (content, parentId) => {
    try {
      const res = await axios.post(`${API_URL}/api/community/${post._id}/comments`, 
        { content, parent_id: parentId },
        { withCredentials: true }
      );
      setComments([...comments, res.data]);
    } catch (error) {
      console.error('Error posting comment:', error);
      throw error;
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await axios.delete(`${API_URL}/api/community/${post._id}/comments/${commentId}`, {
        withCredentials: true
      });
      setComments(comments.filter(c => c.id !== commentId));
    } catch (error) {
      console.error('Error deleting comment:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      if (onDelete) {
        await onDelete(post._id);
      }
    }
    setShowMenu(false);
  };

  const timeAgo = post.created_at 
    ? formatDistanceToNow(new Date(post.created_at), { addSuffix: true })
    : 'recently';

  const topicIcon = TOPIC_ICONS[post.topic] || '💬';

  return (
    <article className="post-card animate-slide-up" data-testid={`community-post-${post._id}`}>
      <header className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 md:gap-3">
          <button 
            onClick={() => onViewProfile && onViewProfile(post.user_id)}
            className="w-10 h-10 md:w-12 md:h-12 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] font-semibold text-base md:text-lg flex-shrink-0 hover:ring-2 hover:ring-[var(--brand-primary)] transition-all cursor-pointer"
            data-testid={`community-post-avatar-${post._id}`}
          >
            {post.user_avatar ? (
              <img src={post.user_avatar} alt="" className="w-full h-full object-cover" />
            ) : (
              post.user_name?.charAt(0)?.toUpperCase() || 'U'
            )}
          </button>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <button 
                onClick={() => onViewProfile && onViewProfile(post.user_id)}
                className="font-medium text-[var(--text-primary)] text-sm md:text-base hover:text-[var(--brand-primary)] hover:underline transition-colors cursor-pointer"
              >
                {post.user_name || 'Anonymous'}
              </button>
              {post.is_verified && (
                <span className="verified-badge">
                  <SealCheck size={10} weight="fill" />
                  Verified
                </span>
              )}
              {post.is_network && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[var(--brand-primary)]/20 text-[var(--brand-primary)] text-[10px] rounded-full">
                  <Handshake size={10} weight="fill" />
                  Network
                </span>
              )}
              {post.is_nearby && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[var(--brand-accent)]/20 text-[var(--brand-accent)] text-[10px] rounded-full">
                  <MapPin size={8} weight="fill" />
                  Nearby
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5 text-[10px] md:text-xs text-[var(--text-muted)]">
              <span>{timeAgo}</span>
              {post.user_location && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-0.5 truncate max-w-[100px] md:max-w-none">
                    <MapPin size={10} />
                    {post.user_location}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
        
        {/* Menu */}
        <div className="relative">
          <button 
            onClick={() => setShowMenu(!showMenu)}
            className="btn-ghost p-1.5 hover:bg-[var(--bg-surface-hover)]"
            data-testid={`community-post-menu-${post._id}`}
          >
            <DotsThree size={18} weight="bold" />
          </button>
          
          {showMenu && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setShowMenu(false)} />
              <div className="absolute right-0 mt-1 w-48 bg-[var(--bg-surface)] border border-[var(--border-color)] rounded-lg shadow-xl z-50 overflow-hidden">
                <button
                  onClick={() => {
                    onViewProfile && onViewProfile(post.user_id);
                    setShowMenu(false);
                  }}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                >
                  <User size={16} />
                  View Profile
                </button>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(window.location.origin + '/community?post=' + post._id);
                    setShowMenu(false);
                  }}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                >
                  <Share size={16} />
                  Copy Link
                </button>
                {(isOwner || isAdmin) && (
                  <button
                    onClick={handleDelete}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--brand-danger)] hover:bg-[var(--bg-surface-hover)] transition-colors border-t border-[var(--border-color)]"
                  >
                    <Trash size={16} />
                    Delete Post
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </header>

      {/* Topic Badge */}
      <div className="flex items-center gap-2 mb-2">
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-[var(--bg-surface-hover)] text-[var(--text-secondary)] text-xs rounded">
          <span>{topicIcon}</span>
          <span className="capitalize">{post.topic?.replace('-', ' ') || 'General'}</span>
        </span>
        {post.is_pinned && (
          <span className="px-2 py-1 bg-[var(--brand-primary)]/20 text-[var(--brand-primary)] text-xs rounded">
            📌 Pinned
          </span>
        )}
      </div>

      {/* Title */}
      <h3 className="text-base md:text-lg font-semibold text-[var(--text-primary)] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
        {post.title}
      </h3>
      
      {/* Content */}
      <div className="relative">
        <p 
          className={`text-sm md:text-base text-[var(--text-secondary)] mb-3 leading-relaxed whitespace-pre-wrap ${
            !expanded && isLongPost ? 'line-clamp-4' : ''
          }`}
        >
          {post.content}
        </p>
        
        {isLongPost && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-[var(--brand-primary)] hover:underline font-medium flex items-center gap-1 -mt-1 mb-3"
          >
            {expanded ? (
              <>Show less <CaretUp size={14} /></>
            ) : (
              <>Read more <CaretDown size={14} /></>
            )}
          </button>
        )}
      </div>

      {/* Images */}
      {post.images?.length > 0 && (
        <div className="mb-3 grid grid-cols-2 gap-2">
          {post.images.slice(0, 4).map((img, i) => (
            <img 
              key={`img-${i}`} 
              src={img.startsWith('/api') ? `${API_URL}${img}` : img} 
              alt={`Post image ${i + 1}`}
              className="w-full h-32 md:h-40 object-cover rounded border border-[var(--border-color)]"
            />
          ))}
        </div>
      )}

      {/* Footer */}
      <footer className="flex items-center gap-4 pt-3 border-t border-[var(--border-color)]">
        <button 
          onClick={handleLikeClick}
          className={`btn-ghost flex items-center gap-2 px-3 ${liked ? 'text-[var(--brand-primary)]' : ''}`}
          data-testid={`like-community-post-${post._id}`}
        >
          <Heart size={18} weight={liked ? 'fill' : 'regular'} />
          <span className="text-sm">{likeCount}</span>
        </button>
        <button 
          onClick={toggleComments}
          className="btn-ghost flex items-center gap-2 px-3"
          data-testid={`toggle-community-comments-${post._id}`}
        >
          <ChatCircle size={18} />
          <span className="text-sm">{comments.length}</span>
          {showComments ? <CaretUp size={12} /> : <CaretDown size={12} />}
        </button>
      </footer>

      {/* Comments Section */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-[var(--border-color)]">
          <div className="max-h-80 overflow-y-auto">
            <ThreadedComments
              comments={comments}
              onAddComment={handleAddComment}
              onDeleteComment={handleDeleteComment}
              currentUserId={currentUserId}
              maxDepth={2}
            />
          </div>
        </div>
      )}
    </article>
  );
}
