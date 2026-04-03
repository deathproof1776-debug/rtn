import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { 
  Images, 
  Heart, 
  ChatCircle, 
  PaperPlaneTilt,
  X,
  Play,
  Plus,
  Camera,
  Trash,
  CaretLeft
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Gallery Grid Component
function GalleryGrid({ items, onItemClick, onLike, currentUserId }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
      {items.map((item) => (
        <div
          key={item.id}
          className="relative aspect-square bg-[var(--bg-surface)] rounded-lg overflow-hidden cursor-pointer group"
          onClick={() => onItemClick(item)}
          data-testid={`gallery-item-${item.id}`}
        >
          {item.is_video ? (
            <div className="w-full h-full flex items-center justify-center bg-black">
              <video
                src={`${API_URL}${item.url}`}
                className="w-full h-full object-cover"
                preload="metadata"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-12 h-12 bg-black/60 rounded-full flex items-center justify-center">
                  <Play size={24} weight="fill" className="text-white ml-1" />
                </div>
              </div>
            </div>
          ) : (
            <img
              src={`${API_URL}${item.url}`}
              alt={item.caption || 'Gallery item'}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          )}
          
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onLike(item.id);
              }}
              className="flex items-center gap-1 text-white"
              data-testid={`gallery-like-${item.id}`}
            >
              <Heart 
                size={20} 
                weight={item.is_liked ? "fill" : "regular"} 
                className={item.is_liked ? "text-red-500" : "text-white"}
              />
              <span>{item.like_count}</span>
            </button>
            <div className="flex items-center gap-1 text-white">
              <ChatCircle size={20} />
              <span>{item.comment_count}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Gallery Item Detail Modal
function GalleryItemModal({ item, onClose, onLike, onComment, currentUserId }) {
  const [comment, setComment] = useState('');
  const [comments, setComments] = useState(item.comments || []);
  const [isLiked, setIsLiked] = useState(item.is_liked);
  const [likeCount, setLikeCount] = useState(item.like_count);
  const [submitting, setSubmitting] = useState(false);
  const videoRef = useRef(null);

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

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim() || submitting) return;

    setSubmitting(true);
    try {
      const response = await axios.post(
        `${API_URL}/api/gallery/${item.id}/comment`,
        { content: comment },
        { withCredentials: true }
      );
      setComments([...comments, response.data]);
      setComment('');
      onComment(item.id, response.data);
    } catch (error) {
      console.error('Error commenting:', error);
      toast.error('Failed to add comment');
    } finally {
      setSubmitting(false);
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
        {/* Header - Always on top */}
        <div className="p-3 border-b border-[var(--border-color)] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[var(--brand-primary)] flex items-center justify-center text-white font-bold text-sm">
              {item.user_name?.[0]?.toUpperCase() || '?'}
            </div>
            <span className="font-medium text-[var(--text-primary)]">{item.user_name}</span>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-[var(--bg-surface-hover)] rounded-full">
            <X size={24} className="text-[var(--text-secondary)]" />
          </button>
        </div>

        {/* Content - Scrollable on mobile */}
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
            {/* Caption & Comments */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {item.caption && (
                <div className="text-sm text-[var(--text-primary)]">
                  <span className="font-medium">{item.user_name}</span> {item.caption}
                </div>
              )}
              
              {comments.map((c) => (
                <div key={c.id} className="text-sm">
                  <span className="font-medium text-[var(--text-primary)]">{c.user_name}</span>
                  <span className="text-[var(--text-secondary)] ml-2">{c.content}</span>
                  <p className="text-xs text-[var(--text-muted)] mt-1">
                    {formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}
                  </p>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="p-3 border-t border-[var(--border-color)] shrink-0">
              <div className="flex items-center gap-4 mb-2">
                <button
                  onClick={handleLike}
                  className="flex items-center gap-1"
                  data-testid="gallery-modal-like"
                >
                  <Heart 
                    size={24} 
                    weight={isLiked ? "fill" : "regular"} 
                    className={isLiked ? "text-red-500" : "text-[var(--text-primary)]"}
                  />
                </button>
                <ChatCircle size={24} className="text-[var(--text-primary)]" />
              </div>
              <p className="text-sm font-medium text-[var(--text-primary)] mb-2">
                {likeCount} {likeCount === 1 ? 'like' : 'likes'}
              </p>
              
              {/* Comment input */}
              <form onSubmit={handleComment} className="flex items-center gap-2">
                <input
                  type="text"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Add a comment..."
                  className="flex-1 bg-transparent border-none outline-none text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
                  data-testid="gallery-comment-input"
                />
              <button
                type="submit"
                disabled={!comment.trim() || submitting}
                className="text-[var(--brand-primary)] font-medium text-sm disabled:opacity-50"
                data-testid="gallery-comment-submit"
              >
                <PaperPlaneTilt size={20} />
              </button>
            </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Upload Modal
function UploadModal({ onClose, onUpload }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [caption, setCaption] = useState('');
  const [uploading, setUploading] = useState(false);
  const [isVideo, setIsVideo] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    // Validate file type
    const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const videoTypes = ['video/mp4', 'video/quicktime', 'video/webm', 'video/mpeg'];
    const allowedTypes = [...imageTypes, ...videoTypes];

    if (!allowedTypes.includes(selectedFile.type)) {
      toast.error('Invalid file type. Allowed: JPEG, PNG, GIF, WebP, MP4, MOV, WebM');
      return;
    }

    // Validate file size
    const maxSize = videoTypes.includes(selectedFile.type) ? 100 * 1024 * 1024 : 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      toast.error(`File too large. Max size: ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    setFile(selectedFile);
    setIsVideo(videoTypes.includes(selectedFile.type));
    setPreview(URL.createObjectURL(selectedFile));
  };

  const handleUpload = async () => {
    if (!file || uploading) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('caption', caption);

    try {
      const response = await axios.post(`${API_URL}/api/gallery/upload`, formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Uploaded successfully');
      onUpload(response.data);
      onClose();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80"
      onClick={onClose}
    >
      <div 
        className="bg-[var(--bg-surface)] rounded-lg overflow-hidden max-w-lg w-full"
        onClick={(e) => e.stopPropagation()}
        data-testid="gallery-upload-modal"
      >
        <div className="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
          <h3 className="font-semibold text-[var(--text-primary)]">Upload to Gallery</h3>
          <button onClick={onClose} className="p-1 hover:bg-[var(--bg-surface-hover)] rounded">
            <X size={20} className="text-[var(--text-secondary)]" />
          </button>
        </div>

        <div className="p-4">
          {!preview ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-[var(--border-color)] rounded-lg p-8 text-center cursor-pointer hover:border-[var(--brand-primary)] transition-colors"
            >
              <Camera size={48} className="mx-auto text-[var(--text-muted)] mb-2" />
              <p className="text-[var(--text-secondary)]">Click to select a photo or video</p>
              <p className="text-xs text-[var(--text-muted)] mt-1">
                Images: JPEG, PNG, GIF, WebP (max 10MB)<br />
                Videos: MP4, MOV, WebM (max 100MB)
              </p>
            </div>
          ) : (
            <div className="relative">
              {isVideo ? (
                <video
                  src={preview}
                  className="w-full rounded-lg max-h-64 object-contain bg-black"
                  controls
                />
              ) : (
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full rounded-lg max-h-64 object-contain"
                />
              )}
              <button
                onClick={() => {
                  setFile(null);
                  setPreview(null);
                }}
                className="absolute top-2 right-2 p-1 bg-black/50 rounded-full hover:bg-black/70"
              >
                <X size={16} className="text-white" />
              </button>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp,video/mp4,video/quicktime,video/webm"
            onChange={handleFileSelect}
            className="hidden"
            data-testid="gallery-file-input"
          />

          {preview && (
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Write a caption..."
              className="w-full mt-4 p-3 bg-[var(--bg-main)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-muted)] resize-none"
              rows={2}
              data-testid="gallery-caption-input"
            />
          )}
        </div>

        <div className="p-4 border-t border-[var(--border-color)] flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-4 py-2 bg-[var(--brand-primary)] text-white rounded-lg disabled:opacity-50 flex items-center gap-2"
            data-testid="gallery-upload-submit"
          >
            {uploading ? 'Uploading...' : 'Share'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Main Gallery Component
export default function Gallery({ userId, isOwnProfile = false, onBack }) {
  const { user: currentUser } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [userName, setUserName] = useState('');

  const fetchGallery = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/gallery/${userId}`, {
        withCredentials: true
      });
      setItems(response.data.items);
      setUserName(response.data.user_name);
    } catch (error) {
      console.error('Error fetching gallery:', error);
      toast.error('Failed to load gallery');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchGallery();
  }, [fetchGallery]);

  const handleLike = async (itemId) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/gallery/${itemId}/like`,
        {},
        { withCredentials: true }
      );
      setItems(items.map(item => 
        item.id === itemId 
          ? { ...item, is_liked: response.data.action === 'liked', like_count: response.data.like_count }
          : item
      ));
    } catch (error) {
      console.error('Error liking item:', error);
    }
  };

  const handleItemClick = async (item) => {
    try {
      const response = await axios.get(`${API_URL}/api/gallery/item/${item.id}`, {
        withCredentials: true
      });
      setSelectedItem(response.data);
    } catch (error) {
      console.error('Error fetching item details:', error);
      setSelectedItem(item);
    }
  };

  const handleUploadComplete = (newItem) => {
    setItems([{
      id: newItem.id,
      url: newItem.url,
      is_video: newItem.is_video,
      caption: newItem.caption,
      like_count: 0,
      comment_count: 0,
      is_liked: false,
      created_at: new Date().toISOString()
    }, ...items]);
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm('Delete this item from your gallery?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/gallery/${itemId}`, {
        withCredentials: true
      });
      setItems(items.filter(item => item.id !== itemId));
      setSelectedItem(null);
      toast.success('Item deleted');
    } catch (error) {
      console.error('Error deleting item:', error);
      toast.error('Failed to delete item');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col" data-testid="gallery-panel">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        {onBack && (
          <button 
            onClick={onBack}
            className="p-2 hover:bg-[var(--bg-surface-hover)] rounded-lg"
            data-testid="gallery-back-btn"
          >
            <CaretLeft size={20} className="text-[var(--text-secondary)]" />
          </button>
        )}
        <Images size={24} weight="duotone" className="text-[var(--brand-primary)]" />
        <h2 className="text-xl font-bold text-[var(--text-primary)]">
          {isOwnProfile ? 'My Gallery' : `${userName}'s Gallery`}
        </h2>
        {isOwnProfile && (
          <button
            onClick={() => setShowUpload(true)}
            className="ml-auto p-2 bg-[var(--brand-primary)] text-white rounded-lg hover:opacity-90"
            data-testid="gallery-upload-btn"
          >
            <Plus size={20} />
          </button>
        )}
      </div>

      {/* Gallery Grid */}
      {items.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
          <Images size={64} className="text-[var(--text-muted)] mb-4" />
          <p className="text-[var(--text-secondary)] mb-2">
            {isOwnProfile ? 'Your gallery is empty' : 'No photos or videos yet'}
          </p>
          {isOwnProfile && (
            <button
              onClick={() => setShowUpload(true)}
              className="mt-4 px-4 py-2 bg-[var(--brand-primary)] text-white rounded-lg flex items-center gap-2"
            >
              <Camera size={18} />
              Upload your first photo
            </button>
          )}
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <GalleryGrid 
            items={items} 
            onItemClick={handleItemClick}
            onLike={handleLike}
            currentUserId={currentUser?.id}
          />
        </div>
      )}

      {/* Modals */}
      {selectedItem && (
        <GalleryItemModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
          onLike={(itemId, data) => {
            setItems(items.map(item => 
              item.id === itemId 
                ? { ...item, is_liked: data.action === 'liked', like_count: data.like_count }
                : item
            ));
          }}
          onComment={(itemId, newComment) => {
            setItems(items.map(item => 
              item.id === itemId 
                ? { ...item, comment_count: item.comment_count + 1 }
                : item
            ));
          }}
          currentUserId={currentUser?.id}
        />
      )}

      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUpload={handleUploadComplete}
        />
      )}
    </div>
  );
}
