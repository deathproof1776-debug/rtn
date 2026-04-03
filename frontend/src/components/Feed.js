/**
 * Feed - Main feed component displaying barter posts
 * Refactored with filters and system banner
 */
import { useState, useRef, useCallback, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  ArrowsLeftRight,
  ArrowClockwise
} from '@phosphor-icons/react';
import PostCard from './PostCard';
import FeedFilters from './FeedFilters';
import SystemBanner from './SystemBanner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Barter categories
const BARTER_CATEGORIES = [
  { id: 'goods', name: 'Goods' },
  { id: 'services', name: 'Services' },
  { id: 'skills', name: 'Skills' }
];

export default function Feed({ 
  posts: initialPosts, 
  loading: initialLoading, 
  onCreatePost, 
  onRefresh, 
  onViewProfile, 
  onProposeTrade, 
  onStartChat 
}) {
  const { user } = useAuth();
  const [posts, setPosts] = useState(initialPosts || []);
  const [loading, setLoading] = useState(initialLoading);
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
  const [refreshing, setRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const containerRef = useRef(null);
  const startY = useRef(0);
  const isPulling = useRef(false);

  const PULL_THRESHOLD = 80;

  // Update posts when initialPosts changes
  useEffect(() => {
    if (initialPosts) {
      setPosts(initialPosts);
    }
  }, [initialPosts]);

  useEffect(() => {
    setLoading(initialLoading);
  }, [initialLoading]);

  // Fetch posts with filters
  const fetchFilteredPosts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.nearby) params.append('nearby_only', 'true');
      if (filters.network) params.append('network_only', 'true');
      if (filters.verified) params.append('verified_only', 'true');
      if (filters.hasMedia) params.append('has_media', 'true');
      if (filters.category && filters.category !== 'all') {
        params.append('category', filters.category);
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
      
      const res = await axios.get(`${API_URL}/api/posts?${params.toString()}`, {
        withCredentials: true
      });
      setPosts(res.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Refetch when filters change
  useEffect(() => {
    // Only fetch if filters are not all default
    const hasActiveFilters = filters.nearby || filters.network || filters.verified || 
                            filters.hasMedia ||
                            (filters.category && filters.category !== 'all') ||
                            (filters.timeRange && filters.timeRange !== 'all') ||
                            (filters.sortBy && filters.sortBy !== 'recent') ||
                            (filters.search && filters.search.trim());
    if (hasActiveFilters) {
      fetchFilteredPosts();
    } else if (onRefresh) {
      // Use parent's refresh for default view
      onRefresh();
    }
  }, [filters, fetchFilteredPosts, onRefresh]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

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
      const resistance = 0.4;
      setPullDistance(Math.min(diff * resistance, PULL_THRESHOLD * 1.5));
    }
  }, []);

  const handleTouchEnd = useCallback(async () => {
    if (pullDistance >= PULL_THRESHOLD && !refreshing) {
      setRefreshing(true);
      try {
        await fetchFilteredPosts();
      } finally {
        setRefreshing(false);
      }
    }
    setPullDistance(0);
    isPulling.current = false;
  }, [pullDistance, refreshing, fetchFilteredPosts]);

  const handleLike = async (postId) => {
    try {
      await axios.post(`${API_URL}/api/posts/${postId}/like`, {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleDelete = async (postId) => {
    try {
      await axios.delete(`${API_URL}/api/posts/${postId}`, {
        withCredentials: true
      });
      // Remove from local state
      setPosts(posts.filter(p => p._id !== postId));
    } catch (error) {
      console.error('Error deleting post:', error);
      alert(error.response?.data?.detail || 'Failed to delete post');
    }
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
    <div 
      ref={containerRef}
      data-testid="feed"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="relative"
    >
      {/* System Banner */}
      <SystemBanner />

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

      {/* Header */}
      <div className="flex items-center justify-between mb-4 md:mb-6">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Barter Feed
          </h2>
          <p className="text-xs md:text-sm text-[var(--text-muted)] mt-0.5">Connect. Trade. Thrive.</p>
        </div>
        <button
          onClick={fetchFilteredPosts}
          disabled={refreshing}
          className="btn-ghost p-2"
          title="Refresh"
        >
          <ArrowClockwise size={18} className={refreshing ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Filters */}
      <div className="mb-4">
        <FeedFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          categories={BARTER_CATEGORIES}
          categoryLabel="Category"
        />
      </div>

      {/* Posts */}
      {posts.length === 0 ? (
        <div className="post-card text-center py-12">
          <ArrowsLeftRight size={48} className="mx-auto text-[var(--bg-surface-active)] mb-4" />
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
            {filters.nearby || filters.network || filters.verified ? 'No matching posts found' : 'No barter posts yet'}
          </h3>
          <p className="text-sm text-[var(--text-muted)] mb-4">
            {filters.nearby || filters.network || filters.verified 
              ? 'Try adjusting your filters to see more posts'
              : 'Be the first to share what you can offer or need'
            }
          </p>
          {filters.nearby || filters.network || filters.verified ? (
            <button 
              onClick={() => setFilters({ nearby: false, network: false, verified: false, category: 'all' })} 
              className="btn-ghost text-[var(--brand-primary)]"
            >
              Clear Filters
            </button>
          ) : (
            <button onClick={onCreatePost} className="btn-primary" data-testid="create-first-post">
              Create Your First Post
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard 
              key={post._id} 
              post={post} 
              onLike={handleLike} 
              onDelete={handleDelete}
              currentUserId={user?.id} 
              isAdmin={user?.role === 'admin'}
              onViewProfile={onViewProfile} 
              onProposeTrade={onProposeTrade} 
              onStartChat={onStartChat} 
            />
          ))}
        </div>
      )}
    </div>
  );
}
