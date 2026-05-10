import { Heart, ChatCircle, CaretDown, CaretUp, ArrowsLeftRight } from '@phosphor-icons/react';

export default function PostActions({
  postId,
  liked,
  likeCount,
  commentCount,
  showComments,
  isOwnPost,
  onLikeClick,
  onToggleComments,
  onProposeTrade
}) {
  return (
    <footer className="flex items-center gap-3 md:gap-4 pt-3 md:pt-4 border-t border-[var(--border-color)]">
      <button
        onClick={onLikeClick}
        className={`btn-ghost flex items-center gap-1.5 md:gap-2 px-2 md:px-3 ${liked ? 'text-[var(--brand-primary)]' : ''}`}
        data-testid={`like-post-${postId}`}
      >
        <Heart size={18} weight={liked ? 'fill' : 'regular'} />
        <span className="text-xs md:text-sm">{likeCount}</span>
      </button>
      <button
        onClick={onToggleComments}
        className="btn-ghost flex items-center gap-1.5 md:gap-2 px-2 md:px-3"
        data-testid={`toggle-comments-${postId}`}
      >
        <ChatCircle size={18} />
        <span className="text-xs md:text-sm">{commentCount}</span>
        {showComments ? <CaretUp size={12} /> : <CaretDown size={12} />}
      </button>
      {!isOwnPost && onProposeTrade && (
        <button
          onClick={onProposeTrade}
          className="btn-ghost flex items-center gap-1.5 md:gap-2 px-2 md:px-3 text-[var(--brand-primary)] ml-auto"
          data-testid={`propose-trade-${postId}`}
        >
          <ArrowsLeftRight size={18} />
          <span className="text-xs md:text-sm hidden sm:inline">Propose Trade</span>
        </button>
      )}
    </footer>
  );
}
