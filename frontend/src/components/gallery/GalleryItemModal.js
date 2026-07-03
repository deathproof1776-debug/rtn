import { useState, useRef } from 'react';
import axios from 'axios';
import { Heart, X, Trash } from '@phosphor-icons/react';
import { toast } from 'sonner';
import ThreadedComments from '../ThreadedComments';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function GalleryItemModal({ item, onClose, onLike, onComment, currentUserId, canDelete, onDelete }) {
  const [comments, setComments] = useState(item.comments || []);
  const [isLiked, setIsLiked] = useState(item.is_liked);
  const [likeCount, setLikeCount] = useState(item.like_count);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const videoRef = useRef(null);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await axios.delete(`${API_URL}/api/gallery/${item.id}`, { withCredentials: true });
      toast.success('Gallery item deleted');
      onDelete?.(item.id);
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete item');
      setDeleting(false);
    }
  };

  const handleLike = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/api/gallery/${item.id}/like`,
        {},
        { withCredentials: true }
      );
      setIsLiked(response.data.action === 'liked');
      setLikeCount(response.data.like_count);
      onLike(item.id, response.data);
    } catch (error) {
      console.error('Error liking item:', error);
    }
  };

  const handleAddComment = async (content, parentId) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/gallery/${item.id}/comment`,
        { content, parent_id: parentId },
        { withCredentials: true }
      );
      setComments([...comments, response.data]);
      onComment(item.id, response.data);
    } catch (error) {
      console.error('Error commenting:', error);
      toast.error('Failed to add comment');
      throw error;
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/90"
      onClick={onClose}
    >
      <div
        className="bg-[var(--bg-surface)] rounded-lg overflow-hidden max-w-4xl w-full max-h-[95vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
        data-testid="gallery-item-modal"
      >
        {/* Header */}
        <div className="p-3 border-b border-[var(--border-color)] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[var(--brand-primary)] flex items-center justify-center text-white font-bold text-sm">
              {item.user_name?.[0]?.toUpperCase() || '?'}
            </div>
            <span className="font-medium text-[var(--text-primary)]">{item.user_name}</span>
          </div>
          <div className="flex items-center gap-1">
            {canDelete && (
              <button
                onClick={() => setConfirmingDelete(true)}
                className="p-2 hover:bg-red-500/10 rounded-full"
                title="Delete"
                data-testid="gallery-delete-btn"
              >
                <Trash size={22} className="text-red-400" />
              </button>
            )}
            <button onClick={onClose} className="p-2 hover:bg-[var(--bg-surface-hover)] rounded-full">
              <X size={24} className="text-[var(--text-secondary)]" />
            </button>
          </div>
        </div>

        {confirmingDelete && (
          <div className="p-3 bg-red-500/10 border-b border-red-500/30 flex items-center justify-between gap-3 shrink-0">
            <span className="text-sm text-[var(--text-primary)]">Delete this item permanently?</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setConfirmingDelete(false)}
                disabled={deleting}
                className="px-3 py-1.5 text-xs border border-[var(--border-color)] text-[var(--text-secondary)] rounded hover:bg-[var(--bg-surface-hover)]"
                data-testid="gallery-delete-cancel"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="px-3 py-1.5 text-xs bg-red-600 hover:bg-red-700 text-white rounded disabled:opacity-60"
                data-testid="gallery-delete-confirm"
              >
                {deleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="flex flex-col md:flex-row flex-1 overflow-hidden">
          {/* Media */}
          <div className="flex-1 bg-black flex items-center justify-center min-h-[200px] max-h-[50vh] md:max-h-none md:min-h-[400px]">
            {item.is_video ? (
              <video
                ref={videoRef}
                src={`${API_URL}${item.url}`}
                className="w-full h-full object-contain"
                controls
                autoPlay
                playsInline
              />
            ) : (
              <img
                src={`${API_URL}${item.url}`}
                alt={item.caption || 'Gallery item'}
                className="max-w-full max-h-full object-contain"
              />
            )}
          </div>

          {/* Details sidebar */}
          <div className="w-full md:w-80 flex flex-col border-t md:border-t-0 md:border-l border-[var(--border-color)] max-h-[40vh] md:max-h-none">
            {item.caption && (
              <div className="p-3 border-b border-[var(--border-color)]">
                <p className="text-sm text-[var(--text-primary)]">
                  <span className="font-medium">{item.user_name}</span> {item.caption}
                </p>
              </div>
            )}

            <div className="p-3 border-b border-[var(--border-color)] flex items-center gap-4">
              <button
                onClick={handleLike}
                className="flex items-center gap-1"
                data-testid="gallery-modal-like"
              >
                <Heart
                  size={24}
                  weight={isLiked ? 'fill' : 'regular'}
                  className={isLiked ? 'text-red-500' : 'text-[var(--text-primary)]'}
                />
                <span className="text-sm text-[var(--text-primary)]">
                  {likeCount} {likeCount === 1 ? 'like' : 'likes'}
                </span>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-3">
              <ThreadedComments
                comments={comments}
                onAddComment={handleAddComment}
                currentUserId={currentUserId}
                maxDepth={2}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
