/**
 * PostCard - Individual post display component
 * Extracted from Feed.js for better modularity
 */
import { useState } from 'react';
import axios from 'axios';
import { 
  Heart, 
  ChatCircle, 
  DotsThree,
  MapPin,
  Tag,
  ArrowsLeftRight,
  CaretDown,
  CaretUp,
  SealCheck,
  Handshake,
  User,
  ChatText,
  Warning,
  Trash
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';
import ThreadedComments from './ThreadedComments';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PostCard({ 
  post, 
  onLike, 
  currentUserId, 
  onViewProfile, 
  onProposeTrade, 
  onStartChat,
  onDelete,
  isAdmin
}) {
  const [liked, setLiked] = useState(post.likes?.includes(currentUserId));
  const [likeCount, setLikeCount] = useState(post.likes?.length || 0);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState(post.comments || []);
  const [loadingComments, setLoadingComments] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

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

  const handleAddComment = async (content, parentId) => {
    try {
      const res = await axios.post(`${API_URL}/api/posts/${post._id}/comments`, 
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
                {post.user_id !== currentUserId && (
                  <>
                    <button
                      onClick={() => {
                        if (onProposeTrade) {
                          onProposeTrade(post.user_id, post.user_name);
                        }
                        setShowMenu(false);
                      }}
                      className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                      data-testid={`post-menu-trade-${post._id}`}
                    >
                      <ArrowsLeftRight size={16} />
                      Propose Trade
                    </button>
                    <button
                      onClick={() => {
                        if (onStartChat) {
                          onStartChat(post.user_id);
                        }
                        setShowMenu(false);
                      }}
                      className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                      data-testid={`post-menu-message-${post._id}`}
                    >
                      <ChatText size={16} />
                      Send Message
                    </button>
                  </>
                )}
                {post.user_id !== currentUserId && (
                  <button
                    onClick={() => {
                      setShowMenu(false);
                    }}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--brand-danger)] hover:bg-[var(--bg-surface-hover)] transition-colors border-t border-[var(--border-color)]"
                    data-testid={`post-menu-report-${post._id}`}
                  >
                    <Warning size={16} />
                    Report Post
                  </button>
                )}
                {/* Delete option for own posts or admin */}
                {(post.user_id === currentUserId || isAdmin) && onDelete && (
                  <button
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
                        onDelete(post._id);
                      }
                      setShowMenu(false);
                    }}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[var(--brand-danger)] hover:bg-[var(--bg-surface-hover)] transition-colors border-t border-[var(--border-color)]"
                    data-testid={`post-menu-delete-${post._id}`}
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

      <h3 className="text-base md:text-lg font-semibold text-[var(--text-primary)] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
        {post.title}
      </h3>
      
      {/* Expandable Post Content */}
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
            {post.offering?.map((item, i) => {
              const itemData = typeof item === 'string' ? { name: item } : item;
              return (
                <span 
                  key={`offer-${itemData.name || item}-${i}`} 
                  className="badge badge-offering text-[10px] md:text-xs"
                  title={itemData.description || itemData.quantity ? `${itemData.quantity || ''} ${itemData.description || ''}`.trim() : ''}
                >
                  {itemData.name || item}
                  {itemData.quantity && <span className="ml-1 opacity-75">({itemData.quantity})</span>}
                </span>
              );
            })}
          </div>
        </div>
        <div className="bg-[var(--bg-main)] p-2.5 md:p-3 border border-[var(--border-color)]">
          <div className="flex items-center gap-1.5 md:gap-2 mb-1.5 md:mb-2">
            <ArrowsLeftRight size={14} className="text-[var(--brand-primary)]" />
            <span className="text-[10px] md:text-xs uppercase tracking-wider text-[var(--brand-primary)] font-semibold">Looking For</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {post.looking_for?.map((item, i) => {
              const itemData = typeof item === 'string' ? { name: item } : item;
              return (
                <span 
                  key={`look-${itemData.name || item}-${i}`} 
                  className="badge badge-looking text-[10px] md:text-xs"
                  title={itemData.description || itemData.quantity ? `${itemData.quantity || ''} ${itemData.description || ''}`.trim() : ''}
                >
                  {itemData.name || item}
                  {itemData.quantity && <span className="ml-1 opacity-75">({itemData.quantity})</span>}
                </span>
              );
            })}
          </div>
        </div>
      </div>

      {post.images?.length > 0 && (
        <div className="mb-3 md:mb-4 grid grid-cols-2 gap-1.5 md:gap-2">
          {post.images.slice(0, 4).map((img, i) => (
            <img 
              key={`img-${img.slice(-20)}-${i}`} 
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
        {post.user_id !== currentUserId && onProposeTrade && (
          <button 
            onClick={() => onProposeTrade(post.user_id, post.user_name)}
            className="btn-ghost flex items-center gap-1.5 md:gap-2 px-2 md:px-3 text-[var(--brand-primary)] ml-auto"
            data-testid={`propose-trade-${post._id}`}
          >
            <ArrowsLeftRight size={18} />
            <span className="text-xs md:text-sm hidden sm:inline">Propose Trade</span>
          </button>
        )}
      </footer>

      {/* Comments Section */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-[var(--border-color)]" data-testid={`comments-section-${post._id}`}>
          {loadingComments ? (
            <div className="flex items-center justify-center py-4">
              <div className="w-5 h-5 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : (
            <div className="max-h-80 overflow-y-auto">
              <ThreadedComments
                comments={comments}
                onAddComment={handleAddComment}
                onDeleteComment={handleDeleteComment}
                currentUserId={currentUserId}
                maxDepth={2}
              />
            </div>
          )}
        </div>
      )}
    </article>
  );
}
