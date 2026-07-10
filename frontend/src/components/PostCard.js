/**
 * PostCard - Individual post display component
 */
import { useState } from 'react';
import axios from 'axios';
import {
  MapPin,
  Tag,
  ArrowsLeftRight,
  CaretDown,
  CaretUp,
  SealCheck,
  Handshake
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner';
import { linkifyText } from '../lib/linkify';
import ThreadedComments from './ThreadedComments';
import PostMedia from './post/PostMedia';
import PostActions from './post/PostActions';
import PostMenu from './post/PostMenu';
import ReportModal from './moderation/ReportModal';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PostCard({
  post,
  onLike,
  currentUserId,
  onViewProfile,
  onProposeTrade,
  onStartChat,
  onDelete,
  onEdit,
  isAdmin
}) {
  const [liked, setLiked] = useState(post.likes?.includes(currentUserId));
  const [likeCount, setLikeCount] = useState(post.likes?.length || 0);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState(post.comments || []);
  const [loadingComments, setLoadingComments] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [showReport, setShowReport] = useState(false);

  const isLongPost = post.description && post.description.length > 200;
  const isOwner = post.user_id === currentUserId;
  const isOtherUser = post.user_id !== currentUserId;

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
      const res = await axios.post(
        `${API_URL}/api/posts/${post._id}/comments`,
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

  const handleEditComment = async (commentId, newContent) => {
    try {
      const res = await axios.put(
        `${API_URL}/api/posts/${post._id}/comments/${commentId}`,
        { content: newContent },
        { withCredentials: true }
      );
      setComments(comments.map(c =>
        c.id === commentId
          ? { ...c, content: res.data.content, updated_at: res.data.updated_at }
          : c
      ));
    } catch (error) {
      console.error('Error editing comment:', error);
    }
  };

  const handleProfileClick = () => {
    if (onViewProfile && post.user_id) {
      onViewProfile(post.user_id);
    }
    setShowMenu(false);
  };

  const handleBlockUser = async () => {
    setShowMenu(false);
    if (!post.user_id) return;
    if (!window.confirm(`Block ${post.user_name || 'this user'}? You will no longer see their posts and they won't see yours.`)) return;
    try {
      await axios.post(
        `${API_URL}/api/moderation/block/${post.user_id}`,
        {},
        { withCredentials: true }
      );
      toast.success('User blocked');
      // Hide locally via onDelete-style callback fallback: dispatch a custom event for parents to refresh
      window.dispatchEvent(new CustomEvent('rtn:user-blocked', { detail: { userId: post.user_id } }));
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to block');
    }
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
            className="w-10 h-10 md:w-12 md:h-12 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] font-semibold text-base md:text-lg flex-shrink-0 hover:ring-2 hover:ring-[var(--brand-primary)] transition-all cursor-pointer overflow-hidden"
            data-testid={`post-avatar-${post._id}`}
            title={`View ${post.user_name}'s profile`}
          >
            {post.user_avatar ? (
              <img src={post.user_avatar} alt={post.user_name} className="w-full h-full object-cover" />
            ) : (
              post.user_name?.charAt(0)?.toUpperCase() || 'U'
            )}
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
                  Verified
                </span>
              )}
              {post.is_trusted_trader && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-green-600/20 text-green-500 text-[10px] md:text-xs rounded-full whitespace-nowrap" data-testid={`trusted-badge-${post._id}`}>
                  <SealCheck size={10} weight="fill" />
                  Trusted
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

        <PostMenu
          postId={post._id}
          isOpen={showMenu}
          setOpen={setShowMenu}
          isOwner={isOwner}
          isAdmin={isAdmin}
          isOtherUser={isOtherUser}
          onViewProfile={handleProfileClick}
          onProposeTrade={() => {
            if (onProposeTrade) onProposeTrade(post.user_id, post.user_name);
            setShowMenu(false);
          }}
          onStartChat={() => {
            if (onStartChat) onStartChat(post.user_id);
            setShowMenu(false);
          }}
          onEdit={onEdit ? () => { onEdit(post); setShowMenu(false); } : null}
          onDelete={onDelete ? () => {
            if (window.confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
              onDelete(post._id);
            }
            setShowMenu(false);
          } : null}
          onReport={() => { setShowReport(true); setShowMenu(false); }}
          onBlock={handleBlockUser}
        />
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
          {linkifyText(post.description)}
        </p>

        {isLongPost && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-[var(--brand-primary)] hover:underline font-medium flex items-center gap-1 -mt-2 mb-3"
            data-testid={`post-expand-btn-${post._id}`}
          >
            {expanded ? (<>Show less <CaretUp size={14} /></>) : (<>Read more <CaretDown size={14} /></>)}
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

      <PostMedia images={post.images} testId={`post-media-${post._id}`} />

      <PostActions
        postId={post._id}
        liked={liked}
        likeCount={likeCount}
        commentCount={comments.length}
        showComments={showComments}
        isOwnPost={isOwner}
        onLikeClick={handleLikeClick}
        onToggleComments={toggleComments}
        onProposeTrade={onProposeTrade ? () => onProposeTrade(post.user_id, post.user_name) : null}
      />

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
                onEditComment={handleEditComment}
                currentUserId={currentUserId}
                maxDepth={2}
              />
            </div>
          )}
        </div>
      )}

      {showReport && (
        <ReportModal
          targetType="post"
          targetId={post._id}
          onClose={() => setShowReport(false)}
        />
      )}
    </article>
  );
}
