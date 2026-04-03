/**
 * CreateCommunityPostModal - Modal for creating new community posts
 * Supports both image and video uploads
 */
import { useState } from 'react';
import axios from 'axios';
import { X, Image as ImageIcon, Upload, VideoCamera, Play } from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CreateCommunityPostModal({ topics, onClose, onPostCreated }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [topic, setTopic] = useState('general');
  const [media, setMedia] = useState([]); // [{url, isVideo, type}]
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleMediaUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    
    if (media.length + files.length > 5) {
      setError('Maximum 5 media files allowed');
      return;
    }

    setUploading(true);
    setError('');

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', 'community');

        const res = await axios.post(`${API_URL}/api/upload`, formData, {
          withCredentials: true,
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        const isVideo = res.data.is_video || file.type.startsWith('video/');
        setMedia(prev => [...prev, {
          url: res.data.url,
          isVideo: isVideo,
          type: file.type
        }]);
      } catch (err) {
        console.error('Upload error:', err);
        setError(err.response?.data?.detail || 'Failed to upload file');
      }
    }

    setUploading(false);
  };

  const removeMedia = (index) => {
    setMedia(media.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      // Send media as array of objects with url and isVideo flag
      const res = await axios.post(`${API_URL}/api/community`, {
        title: title.trim(),
        content: content.trim(),
        topic,
        images: media.map(m => m.url), // Backend still uses 'images' field
        media: media // Send full media info for future use
      }, { withCredentials: true });

      // Fetch the created post to get full data
      const postRes = await axios.get(`${API_URL}/api/community/${res.data.id}`, {
        withCredentials: true
      });

      onPostCreated(postRes.data);
    } catch (err) {
      console.error('Error creating post:', err);
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" data-testid="create-community-modal">
      <div className="bg-[var(--bg-surface)] w-full max-w-xl rounded-lg shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)]">
          <h3 className="text-lg font-semibold text-[var(--text-primary)]">
            New Community Post
          </h3>
          <button onClick={onClose} className="p-2 hover:bg-[var(--bg-surface-hover)] rounded">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-3 bg-red-900/30 border border-red-600 text-red-400 text-sm rounded">
              {error}
            </div>
          )}

          {/* Topic Selection */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
              Topic
            </label>
            <select
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full px-3 py-2 bg-[var(--bg-main)] border border-[var(--border-color)] rounded text-[var(--text-primary)] focus:border-[var(--brand-primary)] focus:outline-none"
              data-testid="community-post-topic"
            >
              {topics.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What's on your mind?"
              className="w-full px-3 py-2 bg-[var(--bg-main)] border border-[var(--border-color)] rounded text-[var(--text-primary)] focus:border-[var(--brand-primary)] focus:outline-none"
              maxLength={200}
              data-testid="community-post-title"
            />
          </div>

          {/* Content */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
              Content
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share your thoughts, tips, questions, or experiences..."
              rows={6}
              className="w-full px-3 py-2 bg-[var(--bg-main)] border border-[var(--border-color)] rounded text-[var(--text-primary)] focus:border-[var(--brand-primary)] focus:outline-none resize-none"
              data-testid="community-post-content"
            />
          </div>

          {/* Media Upload - Images and Videos */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              Media (optional, max 5 images or videos)
            </label>
            
            {media.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {media.map((item, i) => (
                  <div key={i} className="relative">
                    {item.isVideo ? (
                      <div className="w-20 h-20 bg-[var(--bg-surface-hover)] rounded border border-[var(--border-color)] flex items-center justify-center">
                        <Play size={24} className="text-[var(--brand-primary)]" weight="fill" />
                      </div>
                    ) : (
                      <img 
                        src={item.url.startsWith('/api') ? `${API_URL}${item.url}` : item.url} 
                        alt={`Upload ${i + 1}`}
                        className="w-20 h-20 object-cover rounded border border-[var(--border-color)]"
                      />
                    )}
                    <button
                      type="button"
                      onClick={() => removeMedia(i)}
                      className="absolute -top-2 -right-2 p-1 bg-red-600 rounded-full text-white"
                    >
                      <X size={12} />
                    </button>
                    {item.isVideo && (
                      <span className="absolute bottom-1 left-1 text-[8px] bg-black/70 text-white px-1 rounded">
                        VIDEO
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {media.length < 5 && (
              <label className="flex items-center justify-center gap-2 p-4 border-2 border-dashed border-[var(--border-color)] rounded cursor-pointer hover:border-[var(--brand-primary)] transition-colors">
                {uploading ? (
                  <div className="w-5 h-5 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <ImageIcon size={20} className="text-[var(--text-muted)]" />
                    <VideoCamera size={20} className="text-[var(--text-muted)]" />
                    <span className="text-sm text-[var(--text-muted)]">Add images or videos</span>
                  </>
                )}
                <input
                  type="file"
                  accept="image/*,video/*"
                  multiple
                  onChange={handleMediaUpload}
                  className="hidden"
                  disabled={uploading}
                  data-testid="community-media-upload"
                />
              </label>
            )}
            <p className="text-xs text-[var(--text-muted)] mt-1">
              Supported: JPEG, PNG, GIF, WebP, MP4, MOV, WebM (max 10MB images, 100MB videos)
            </p>
          </div>

          {/* Submit */}
          <div className="flex justify-end gap-3 pt-4 border-t border-[var(--border-color)]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] rounded transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !title.trim() || !content.trim()}
              className="btn-primary flex items-center gap-2"
              data-testid="submit-community-post"
            >
              {submitting ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Upload size={16} />
              )}
              Post
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
