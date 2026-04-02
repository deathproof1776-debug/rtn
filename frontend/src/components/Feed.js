import { useState, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  Heart, 
  ChatCircle, 
  DotsThree,
  MapPin,
  Tag,
  ArrowsLeftRight,
  PaperPlaneTilt,
  Trash,
  CaretDown,
  CaretUp,
  ArrowClockwise,
  SealCheck,
  Handshake,
  User,
  ChatText,
  Warning,
  X
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Feed({ posts, loading, onCreatePost, onFilterChange, nearbyOnly = false, onRefresh, onViewProfile }) {
  const { user } = useAuth();
  const [filterNearby, setFilterNearby] = useState(nearbyOnly);
  const [refreshing, setRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const containerRef = useRef(null);
  const startY = useRef(0);
  const isPulling = useRef(false);

  const PULL_THRESHOLD = 80;

  const handleTouchStart = useCallback((e) => {
    const container = containerRef.current;
    if (container && container.scrollTop === 0) {
      startY.current = e.touches[0].clientY;
      isPulling.current = true;
    }
  }, []);

  const handleTouchMove = useCallback((e) => {
    if (!isPulling.current) return;
    
    const currentY = e.touches[0].clientY;
    const diff = currentY - startY.current;
    
    if (diff > 0) {
      // Apply resistance to the pull
      const resistance = 0.4;
      setPullDistance(Math.min(diff * resistance, PULL_THRESHOLD * 1.5));
    }
  }, []);

  const handleTouchEnd = useCallback(async () => {
    if (pullDistance >= PULL_THRESHOLD && onRefresh && !refreshing) {
      setRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setRefreshing(false);
      }
    }
    setPullDistance(0);
    isPulling.current = false;
  }, [pullDistance, onRefresh, refreshing]);

  const handleLike = async (postId) => {
    try {
      await axios.post(`${API_URL}/api/posts/${postId}/like`, {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleFilterToggle = () => {
    const newValue = !filterNearby;
    setFilterNearby(newValue);
    if (onFilterChange) {
      onFilterChange(newValue);
    }
  };

  // Filter posts if nearby filter is active
  const displayPosts = filterNearby 
    ? posts.filter(post => post.is_nearby)
    : posts;

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="post-card animate-pulse">
            <div className="h-4 bg-[var(--bg-surface-hover)] w-1/3 mb-4"></div>
            <div className="h-3 bg-[var(--bg-surface-hover)] w-full mb-2"></div>
            <div className="h-3 bg-[var(--bg-surface-hover)] w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      data-testid="feed"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="relative"
    >
      {/* Pull to refresh indicator */}
      <div 
        className="pull-to-refresh-indicator md:hidden"
        style={{ 
          height: pullDistance,
          opacity: Math.min(pullDistance / PULL_THRESHOLD, 1)
        }}
        data-testid="pull-to-refresh-indicator"
      >
        <div className={`pull-to-refresh-content ${refreshing ? 'refreshing' : ''} ${pullDistance >= PULL_THRESHOLD ? 'ready' : ''}`}>
          <ArrowClockwise 
            size={24} 
            weight="bold"
            className={refreshing ? 'animate-spin' : ''}
            style={{ 
              transform: refreshing ? 'none' : `rotate(${Math.min(pullDistance / PULL_THRESHOLD * 180, 180)}deg)`,
              transition: refreshing ? 'none' : 'transform 0.1s ease-out'
            }}
          />
          <span className="text-xs mt-1">
            {refreshing ? 'Refreshing...' : pullDistance >= PULL_THRESHOLD ? 'Release to refresh' : 'Pull to refresh'}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4 md:mb-8">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Barter Feed
          </h2>
          <p className="text-xs md:text-sm text-[var(--text-muted)] mt-0.5 md:mt-1">Connect. Trade. Thrive.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleFilterToggle}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 md:px-3 md:py-2 text-xs md:text-sm border transition-all ${
              filterNearby 
                ? 'bg-[var(--brand-primary)] border-[var(--brand-primary)] text-white' 
                : 'bg-transparent border-[var(--bg-surface-active)] text-[var(--text-secondary)] hover:border-[var(--brand-primary)] hover:text-[var(--brand-primary)]'
            }`}
            data-testid="filter-nearby-btn"
          >
            <MapPin size={14} weight={filterNearby ? 'fill' : 'regular'} />
            <span className="hidden sm:inline">Nearby</span>
          </button>
        </div>
      </div>

      {displayPosts.length === 0 ? (
        <div className="post-card text-center py-12">
          {filterNearby ? (
            <>
              <MapPin size={48} className="mx-auto text-[var(--bg-surface-active)] mb-4" />
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">No nearby posts found</h3>
              <p className="text-sm text-[var(--text-muted)] mb-4">
                Try expanding your search or update your location in your profile
              </p>
              <button onClick={handleFilterToggle} className="btn-ghost text-[var(--brand-primary)]" data-testid="show-all-posts-btn">
                Show All Posts
              </button>
            </>
          ) : (
            <>
              <ArrowsLeftRight size={48} className="mx-auto text-[var(--bg-surface-active)] mb-4" />
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">No barter posts yet</h3>
              <p className="text-sm text-[var(--text-muted)] mb-4">Be the first to share what you can offer or need</p>
              <button onClick={onCreatePost} className="btn-primary" data-testid="create-first-post">
                Create Your First Post
              </button>
            </>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {displayPosts.map((post) => (
            <PostCard key={post._id} post={post} onLike={handleLike} currentUserId={user?.id} onViewProfile={onViewProfile} />
          ))}
        </div>
      )}
    </div>
  );
}

function PostCard({ post, onLike, currentUserId, onViewProfile }) {
  const [liked, setLiked] = useState(post.likes?.includes(currentUserId));
  const [likeCount, setLikeCount] = useState(post.likes?.length || 0);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState(post.comments || []);
  const [newComment, setNewComment] = useState('');
  const [loadingComments, setLoadingComments] = useState(false);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  // Check if post content is long enough to need expansion
  const isLongPost = post.description && post.description.length > 200;

  const handleLikeClick = async () => {
    await onLike(post._id);
    setLiked(!liked);
    setLikeCount(liked ? likeCount - 1 : likeCount + 1);
  };

  const fetchComments = async () => {
    setLoadingComments(true);
    try {
      const res = await axios.get(`${API_URL}/api/posts/${post._id}/comments`, {
        withCredentials: true
      });
      setComments(res.data);
    } catch (error) {
      console.error('Error fetching comments:', error);
    } finally {
      setLoadingComments(false);
    }
  };

  const toggleComments = () => {
    if (!showComments && comments.length === 0) {
      fetchComments();
    }
    setShowComments(!showComments);
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    
    setSubmittingComment(true);
    try {
      const res = await axios.post(`${API_URL}/api/posts/${post._id}/comments`, 
        { content: newComment },
        { withCredentials: true }
      );
      setComments([...comments, res.data]);
      setNewComment('');
    } catch (error) {
      console.error('Error posting comment:', error);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await axios.delete(`${API_URL}/api/posts/${post._id}/comments/${commentId}`, {
        withCredentials: true
      });
      setComments(comments.filter(c => c.id !== commentId));
    } catch (error) {
      console.error('Error deleting comment:', error);
    }
  };

  const handleProfileClick = () => {
    if (onViewProfile && post.user_id) {
      onViewProfile(post.user_id);
    }
    setShowMenu(false);
  };

  const timeAgo = post.created_at 
    ? formatDistanceToNow(new Date(post.created_at), { addSuffix: true })
    : 'recently';

  return (
    <article className="post-card animate-slide-up" data-testid={`post-${post._id}`}>
      <header className="flex items-start justify-between mb-3 md:mb-4">
        <div className="flex items-center gap-2 md:gap-3">
          {/* Clickable Avatar */}
          <button 
            onClick={handleProfileClick}
            className="w-10 h-10 md:w-12 md:h-12 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] font-semibold text-base md:text-lg flex-shrink-0 hover:ring-2 hover:ring-[var(--brand-primary)] transition-all cursor-pointer"
            data-testid={`post-avatar-${post._id}`}
            title={`View ${post.user_name}'s profile`}
          >
            {post.user_name?.charAt(0)?.toUpperCase() || 'U'}
          </button>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 md:gap-2 flex-wrap">
              {/* Clickable Username */}
              <button 
                onClick={handleProfileClick}
                className="font-medium text-[var(--text-primary)] text-sm md:text-base hover:text-[var(--brand-primary)] hover:underline transition-colors cursor-pointer"
                data-testid={`post-username-${post._id}`}
              >
                {post.user_name || 'Anonymous'}
              </button>
              {post.is_verified && (
                <span className="verified-badge" data-testid={`verified-badge-${post._id}`}>
                  <SealCheck size={10} weight="fill" />
                  Verified Trader
                </span>
              )}
              {post.is_network && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[var(--brand-primary)]/20 text-[var(--brand-primary)] text-[10px] md:text-xs rounded-full whitespace-nowrap" data-testid={`network-badge-${post._id}`}>
                  <Handshake size={10} weight="fill" />
                  Network
                </span>
              )}
              {post.is_nearby && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[var(--brand-accent)]/20 text-[var(--brand-accent)] text-[10px] md:text-xs rounded-full whitespace-nowrap" data-testid={`nearby-badge-${post._id}`}>
                  <MapPin size={8} weight="fill" />
                  Nearby
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5 md:gap-2 text-[10px] md:text-xs text-[var(--text-muted)]">
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
        
        {/* 3 Dots Menu */}
        <div className="relative">
          <button 
            onClick={() => setShowMenu(!showMenu)}
            className="btn-ghost p-1.5 md:p-2 flex-shrink-0 hover:bg-[var(--bg-surface-hover)]"
            data-testid={`post-menu-btn-${post._id}`}
          >
            <DotsThree size={18} weight="bold" />
          </button>
          
          {showMenu && (
            <>
              <div 
                className="fixed inset-0 z-40" 
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 mt-1 w-48 bg-[var(--bg-surface)] border border-[var(--border-color)] rounded-lg shadow-xl z-50 overflow-hidden" data-testid={`post-menu-dropdown-${post._id}`}>
                <button
                  onClick={handleProfileClick}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                  data-testid={`post-menu-view-profile-${post._id}`}
                >
                  <User size={16} />
                  View Profile
                </button>
                <button
                  onClick={() => {
                    // Could open messaging with this user in future
                    setShowMenu(false);
                  }}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                  data-testid={`post-menu-message-${post._id}`}
                >
                  <ChatText size={16} />
                  Send Message
                </button>
                <button
                  onClick={() => {
                    // Report functionality - future feature
                    setShowMenu(false);
                  }}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--brand-danger)] hover:bg-[var(--bg-surface-hover)] transition-colors border-t border-[var(--border-color)]"
                  data-testid={`post-menu-report-${post._id}`}
                >
                  <Warning size={16} />
                  Report Post
                </button>
              </div>
            </>
          )}
        </div>
      </header>

      <h3 className="text-base md:text-lg font-semibold text-[var(--text-primary)] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
        {post.title}
      </h3>
      
      {/* Expandable/Collapsible Post Content */}
      <div className="relative">
        <p 
          className={`text-sm md:text-base text-[var(--text-secondary)] mb-3 md:mb-4 leading-relaxed ${
            !expanded && isLongPost ? 'line-clamp-3' : ''
          }`}
          data-testid={`post-description-${post._id}`}
        >
          {post.description}
        </p>
        
        {isLongPost && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-[var(--brand-primary)] hover:underline font-medium flex items-center gap-1 -mt-2 mb-3"
            data-testid={`post-expand-btn-${post._id}`}
          >
            {expanded ? (
              <>
                Show less <CaretUp size={14} />
              </>
            ) : (
              <>
                Read more <CaretDown size={14} />
              </>
            )}
          </button>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5 md:gap-2 mb-3 md:mb-4">
        <span className="badge text-[10px] md:text-xs">{post.category?.toUpperCase()}</span>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 md:gap-4 mb-3 md:mb-4">
        <div className="bg-[var(--bg-main)] p-2.5 md:p-3 border border-[var(--border-color)]">
          <div className="flex items-center gap-1.5 md:gap-2 mb-1.5 md:mb-2">
            <Tag size={14} className="text-[var(--brand-accent)]" />
            <span className="text-[10px] md:text-xs uppercase tracking-wider text-[var(--brand-accent)] font-semibold">Offering</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {post.offering?.map((item, i) => (
              <span key={i} className="badge badge-offering text-[10px] md:text-xs">{item}</span>
            ))}
          </div>
        </div>
        <div className="bg-[var(--bg-main)] p-2.5 md:p-3 border border-[var(--border-color)]">
          <div className="flex items-center gap-1.5 md:gap-2 mb-1.5 md:mb-2">
            <ArrowsLeftRight size={14} className="text-[var(--brand-primary)]" />
            <span className="text-[10px] md:text-xs uppercase tracking-wider text-[var(--brand-primary)] font-semibold">Looking For</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {post.looking_for?.map((item, i) => (
              <span key={i} className="badge badge-looking text-[10px] md:text-xs">{item}</span>
            ))}
          </div>
        </div>
      </div>

      {post.images?.length > 0 && (
        <div className="mb-3 md:mb-4 grid grid-cols-2 gap-1.5 md:gap-2">
          {post.images.slice(0, 4).map((img, i) => (
            <img 
              key={i} 
              src={img} 
              alt={`Post image ${i + 1}`}
              className="w-full h-24 md:h-32 object-cover border border-[var(--border-color)]"
            />
          ))}
        </div>
      )}

      <footer className="flex items-center gap-3 md:gap-4 pt-3 md:pt-4 border-t border-[var(--border-color)]">
        <button 
          onClick={handleLikeClick}
          className={`btn-ghost flex items-center gap-1.5 md:gap-2 px-2 md:px-3 ${liked ? 'text-[var(--brand-primary)]' : ''}`}
          data-testid={`like-post-${post._id}`}
        >
          <Heart size={18} weight={liked ? 'fill' : 'regular'} />
          <span className="text-xs md:text-sm">{likeCount}</span>
        </button>
        <button 
          onClick={toggleComments}
          className="btn-ghost flex items-center gap-1.5 md:gap-2 px-2 md:px-3"
          data-testid={`toggle-comments-${post._id}`}
        >
          <ChatCircle size={18} />
          <span className="text-xs md:text-sm">{comments.length}</span>
          {showComments ? <CaretUp size={12} /> : <CaretDown size={12} />}
        </button>
      </footer>

      {/* Comments Section */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-[var(--border-color)]" data-testid={`comments-section-${post._id}`}>
          {/* Comment Input */}
          <form onSubmit={handleSubmitComment} className="flex gap-2 mb-4">
            <input
              type="text"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a comment..."
              className="flex-1 bg-[var(--bg-main)] border border-[var(--bg-surface-active)] text-[var(--text-primary)] px-3 py-2 text-sm focus:ring-1 focus:ring-[var(--brand-primary)] focus:border-[var(--brand-primary)] outline-none"
              data-testid={`comment-input-${post._id}`}
            />
            <button 
              type="submit"
              disabled={submittingComment || !newComment.trim()}
              className="btn-primary px-3 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid={`submit-comment-${post._id}`}
            >
              <PaperPlaneTilt size={18} weight="fill" />
            </button>
          </form>

          {/* Comments List */}
          {loadingComments ? (
            <div className="flex items-center justify-center py-4">
              <div className="w-5 h-5 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : comments.length === 0 ? (
            <p className="text-[var(--text-muted)] text-sm text-center py-4">No comments yet. Be the first to comment!</p>
          ) : (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {comments.map((comment) => (
                <CommentItem 
                  key={comment.id} 
                  comment={comment} 
                  currentUserId={currentUserId}
                  postUserId={post.user_id}
                  onDelete={handleDeleteComment}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </article>
  );
}

function CommentItem({ comment, currentUserId, postUserId, onDelete }) {
  const timeAgo = comment.created_at 
    ? formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })
    : 'recently';
  
  const canDelete = comment.user_id === currentUserId || postUserId === currentUserId;

  return (
    <div className="flex gap-3 group" data-testid={`comment-${comment.id}`}>
      <div className="w-8 h-8 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] font-semibold text-xs flex-shrink-0">
        {comment.user_name?.charAt(0)?.toUpperCase() || 'U'}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-[var(--text-primary)]">{comment.user_name}</span>
          <span className="text-xs text-[var(--text-muted)]">{timeAgo}</span>
          {canDelete && (
            <button 
              onClick={() => onDelete(comment.id)}
              className="ml-auto opacity-0 group-hover:opacity-100 text-[var(--brand-danger)] hover:text-red-400 transition-opacity"
              data-testid={`delete-comment-${comment.id}`}
            >
              <Trash size={14} />
            </button>
          )}
        </div>
        <p className="text-sm text-[var(--text-secondary)] break-words">{comment.content}</p>
      </div>
    </div>
  );
}
