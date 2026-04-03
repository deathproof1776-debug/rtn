/**
 * Feed - Main feed component displaying barter posts
 * Refactored to use extracted PostCard component
 */
import { useState, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  MapPin,
  ArrowsLeftRight,
  ArrowClockwise
} from '@phosphor-icons/react';
import PostCard from './PostCard';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Feed({ 
  posts, 
  loading, 
  onCreatePost, 
  onFilterChange, 
  nearbyOnly = false, 
  onRefresh, 
  onViewProfile, 
  onProposeTrade, 
  onStartChat 
}) {
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

  const displayPosts = filterNearby 
    ? posts.filter(post => post.is_nearby)
    : posts;

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
            <PostCard 
              key={post._id} 
              post={post} 
              onLike={handleLike} 
              currentUserId={user?.id} 
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
