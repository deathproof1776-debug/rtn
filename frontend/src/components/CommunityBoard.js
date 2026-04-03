/**
 * CommunityBoard - General discussion forum for homesteading/off-grid community
 */
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  Plus,
  ArrowClockwise,
  Newspaper,
  X,
  Image as ImageIcon,
  Upload
} from '@phosphor-icons/react';
import CommunityPostCard from './CommunityPostCard';
import FeedFilters from './FeedFilters';
import SystemBanner from './SystemBanner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CommunityBoard({ onViewProfile }) {
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [topics, setTopics] = useState([]);
  const [filters, setFilters] = useState({
    nearby: false,
    network: false,
    verified: false,
    hasMedia: false,
    category: 'all',
    timeRange: 'all',
    sortBy: 'recent',
    search: ''
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch topics
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/community/topics`, {
          withCredentials: true
        });
        setTopics(res.data.topics || []);
      } catch (error) {
        console.error('Error fetching topics:', error);
      }
    };
    fetchTopics();
  }, []);

  // Fetch posts
  const fetchPosts = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (filters.nearby) params.append('nearby_only', 'true');
      if (filters.network) params.append('network_only', 'true');
      if (filters.verified) params.append('verified_only', 'true');
      if (filters.hasMedia) params.append('has_media', 'true');
      if (filters.category && filters.category !== 'all') {
        params.append('topic', filters.category);
      }
      if (filters.timeRange && filters.timeRange !== 'all') {
        params.append('time_range', filters.timeRange);
      }
      if (filters.sortBy && filters.sortBy !== 'recent') {
        params.append('sort_by', filters.sortBy);
      }
      if (filters.search && filters.search.trim()) {
        params.append('search', filters.search.trim());
      }
      
      const res = await axios.get(`${API_URL}/api/community?${params.toString()}`, {
        withCredentials: true
      });
      setPosts(res.data);
    } catch (error) {
      console.error('Error fetching community posts:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchPosts();
    setRefreshing(false);
  };

  const handleLike = async (postId) => {
    try {
      await axios.post(`${API_URL}/api/community/${postId}/like`, {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleDelete = async (postId) => {
    try {
      await axios.delete(`${API_URL}/api/community/${postId}`, {
        withCredentials: true
      });
      setPosts(posts.filter(p => p._id !== postId));
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  };

  const handlePostCreated = (newPost) => {
    setPosts([newPost, ...posts]);
    setShowCreateModal(false);
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={`skeleton-${i}`} className="post-card animate-pulse">
            <div className="h-4 bg-[var(--bg-surface-hover)] w-1/3 mb-4"></div>
            <div className="h-3 bg-[var(--bg-surface-hover)] w-full mb-2"></div>
            <div className="h-3 bg-[var(--bg-surface-hover)] w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div data-testid="community-board">
      {/* System Banner */}
      <SystemBanner />

      {/* Header */}
      <div className="flex items-center justify-between mb-4 md:mb-6">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Community Board
          </h2>
          <p className="text-xs md:text-sm text-[var(--text-muted)] mt-0.5">
            Share knowledge. Build community. Exit the system.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn-ghost p-2"
            title="Refresh"
          >
            <ArrowClockwise size={18} className={refreshing ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center gap-2"
            data-testid="create-community-post-btn"
          >
            <Plus size={16} weight="bold" />
            <span className="hidden sm:inline">New Post</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4">
        <FeedFilters
          filters={filters}
          onFilterChange={setFilters}
          categories={topics}
          categoryLabel="Topic"
        />
      </div>

      {/* Posts */}
      {posts.length === 0 ? (
        <div className="post-card text-center py-12">
          <Newspaper size={48} className="mx-auto text-[var(--bg-surface-active)] mb-4" />
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">No posts yet</h3>
          <p className="text-sm text-[var(--text-muted)] mb-4">
            Be the first to share with the community
          </p>
          <button 
            onClick={() => setShowCreateModal(true)} 
            className="btn-primary"
          >
            Create First Post
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <CommunityPostCard
              key={post._id}
              post={post}
              onLike={handleLike}
              currentUserId={user?.id}
              onViewProfile={onViewProfile}
              onDelete={handleDelete}
              isAdmin={user?.role === 'admin'}
            />
          ))}
        </div>
      )}

      {/* Create Post Modal */}
      {showCreateModal && (
        <CreateCommunityPostModal
          topics={topics}
          onClose={() => setShowCreateModal(false)}
          onPostCreated={handlePostCreated}
        />
      )}
    </div>
  );
}


// Create Post Modal Component
function CreateCommunityPostModal({ topics, onClose, onPostCreated }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [topic, setTopic] = useState('general');
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleImageUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    
    if (images.length + files.length > 5) {
      setError('Maximum 5 images allowed');
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

        setImages(prev => [...prev, res.data.url]);
      } catch (err) {
        console.error('Upload error:', err);
        setError('Failed to upload image');
      }
    }

    setUploading(false);
  };

  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
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
      const res = await axios.post(`${API_URL}/api/community`, {
        title: title.trim(),
        content: content.trim(),
        topic,
        images
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

          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              Images (optional, max 5)
            </label>
            
            {images.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {images.map((img, i) => (
                  <div key={i} className="relative">
                    <img 
                      src={img.startsWith('/api') ? `${API_URL}${img}` : img} 
                      alt={`Upload ${i + 1}`}
                      className="w-20 h-20 object-cover rounded border border-[var(--border-color)]"
                    />
                    <button
                      type="button"
                      onClick={() => removeImage(i)}
                      className="absolute -top-2 -right-2 p-1 bg-red-600 rounded-full text-white"
                    >
                      <X size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {images.length < 5 && (
              <label className="flex items-center justify-center gap-2 p-4 border-2 border-dashed border-[var(--border-color)] rounded cursor-pointer hover:border-[var(--brand-primary)] transition-colors">
                {uploading ? (
                  <div className="w-5 h-5 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <ImageIcon size={20} className="text-[var(--text-muted)]" />
                    <span className="text-sm text-[var(--text-muted)]">Add images</span>
                  </>
                )}
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
            )}
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
