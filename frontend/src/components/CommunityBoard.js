/**
 * CommunityBoard - General discussion forum for homesteading/off-grid community
 * Refactored to use modular sub-components
 */
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  Plus,
  ArrowClockwise,
  Newspaper
} from '@phosphor-icons/react';
import CommunityPostCard from './CommunityPostCard';
import FeedFilters from './FeedFilters';
import SystemBanner from './SystemBanner';
import { CreateCommunityPostModal } from './community';

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
