import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { ShieldCheck } from '@phosphor-icons/react';
import Sidebar from '../components/Sidebar';
import Feed from '../components/Feed';
import RightPanel from '../components/RightPanel';
import CreatePostModal from '../components/CreatePostModal';
import MessagesPanel from '../components/MessagesPanel';
import ProfilePanel from '../components/ProfilePanel';
import TradeNetworkPanel from '../components/TradeNetworkPanel';
import TradeDealsPanel from '../components/TradeDealsPanel';
import UserProfileView from '../components/UserProfileView';
import MobileNav from '../components/MobileNav';
import MobileHeader from '../components/MobileHeader';
import InvitePanel from '../components/InvitePanel';
import AdminDashboard from './AdminDashboard';
import CreateTradeModal from '../components/CreateTradeModal';
import Gallery from '../components/Gallery';
import CommunityBoard from '../components/CommunityBoard';
import SecuritySettings from '../components/SecuritySettings';
import ModerationDashboard from './ModerationDashboard';
import OnboardingTour from '../components/OnboardingTour';
import AchievementCelebration from '../components/AchievementCelebration';
import ChangelogModal from '../components/ChangelogModal';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Dashboard() {
  const { user, loading, updateUser } = useAuth();
  const navigate = useNavigate();
  const [activeView, setActiveView] = useState('feed');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [posts, setPosts] = useState([]);
  const [matches, setMatches] = useState([]);
  const [postsLoading, setPostsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [networkRequestCount, setNetworkRequestCount] = useState(0);
  const [tradeDealsCount, setTradeDealsCount] = useState(0);
  const [viewingProfileId, setViewingProfileId] = useState(null);
  const [tradeTarget, setTradeTarget] = useState(null);
  const [chatUserId, setChatUserId] = useState(null);
  const [viewingGallery, setViewingGallery] = useState(null);
  const [editingPost, setEditingPost] = useState(null);
  const [windowFocused, setWindowFocused] = useState(true);
  const [changelog, setChangelog] = useState(null);

  const isPrivileged = user?.role === 'admin' || user?.role === 'moderator';

  // Screenshot prevention: blur content when window loses focus (regular users only)
  useEffect(() => {
    if (isPrivileged) return;
    const onBlur = () => setWindowFocused(false);
    const onFocus = () => setWindowFocused(true);
    window.addEventListener('blur', onBlur);
    window.addEventListener('focus', onFocus);
    return () => {
      window.removeEventListener('blur', onBlur);
      window.removeEventListener('focus', onFocus);
    };
  }, [isPrivileged]);

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

  useEffect(() => {
    if (user && !user.has_seen_onboarding) {
      setShowOnboarding(true);
    }
  }, [user]);

  // Fetch unread changelog for this user
  useEffect(() => {
    if (!user) return;
    axios.get(`${API_URL}/api/changelog/latest`, { withCredentials: true })
      .then(r => { if (r.data?.changelog) setChangelog(r.data.changelog); })
      .catch(() => {});
  }, [user]);

  const pendingAchievements = (user && user.pending_achievements) || [];
  // Tour must complete first; then show achievements one-at-a-time in received order.
  const currentAchievement = (user && user.has_seen_onboarding && !showOnboarding && pendingAchievements.length > 0)
    ? pendingAchievements[0]
    : null;

  const handleAckAchievement = (key) => {
    updateUser({ pending_achievements: pendingAchievements.filter(k => k !== key) });
  };

  const fetchPosts = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/posts`, {
        withCredentials: true
      });
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setPostsLoading(false);
    }
  }, []);

  const fetchMatches = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/posts/matches`, {
        withCredentials: true
      });
      setMatches(response.data);
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  }, []);

  const fetchNetworkRequests = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/network/requests/pending`, {
        withCredentials: true
      });
      setNetworkRequestCount(response.data.incoming_count || 0);
    } catch (error) {
      console.error('Error fetching network requests:', error);
    }
  }, []);

  const fetchTradeDealsCount = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/trades/active-count`, {
        withCredentials: true
      });
      setTradeDealsCount(response.data.count || 0);
    } catch (error) {
      console.error('Error fetching trade deals count:', error);
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetchPosts();
      fetchMatches();
      fetchNetworkRequests();
      fetchTradeDealsCount();
    }
  }, [user, fetchPosts, fetchMatches, fetchNetworkRequests, fetchTradeDealsCount]);

  const handlePostCreated = (newPost) => {
    // Check if this is an update (post already exists in the list)
    const existingIndex = posts.findIndex(p => p._id === newPost._id);
    if (existingIndex >= 0) {
      // Update existing post
      const updatedPosts = [...posts];
      updatedPosts[existingIndex] = newPost;
      setPosts(updatedPosts);
    } else {
      // Add new post
      setPosts([newPost, ...posts]);
    }
    setShowCreatePost(false);
    setEditingPost(null);
  };

  const handleEditPost = (post) => {
    setEditingPost(post);
    setShowCreatePost(true);
  };

  const handleViewProfile = (userId) => {
    setViewingProfileId(userId);
  };

  const handleStartChat = (userId) => {
    setViewingProfileId(null);
    setChatUserId(userId);
    setActiveView('messages');
  };

  const handleProposeTrade = (userId, userName) => {
    setTradeTarget({ userId, userName });
  };

  const handleViewGallery = (userId, userName) => {
    setViewingGallery({ userId, userName });
    setActiveView('gallery');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-main)] flex items-center justify-center">
        <div className="text-[var(--text-secondary)]">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className={`app-shell ${!isPrivileged ? 'screenshot-protected' : ''}`} data-testid="dashboard">
      {/* Watermark for regular users */}
      {!isPrivileged && (
        <div className="rtn-watermark" data-user={user?.name || 'RTN'} aria-hidden="true" />
      )}

      {/* Security blur overlay on window blur (regular users only) */}
      {!isPrivileged && !windowFocused && (
        <div
          className="security-blur-overlay"
          onClick={() => setWindowFocused(true)}
          data-testid="security-blur-overlay"
        >
          <ShieldCheck size={48} className="text-[var(--brand-primary)]" />
          <p className="text-[var(--text-primary)] text-xl font-bold">Paused for Security</p>
          <p className="text-[var(--text-muted)] text-sm">Click anywhere to resume</p>
        </div>
      )}
      {/* Mobile Header */}
      <MobileHeader 
        onMenuClick={() => setSidebarOpen(true)}
        onCreatePost={() => setShowCreatePost(true)}
      />

      {/* Mobile Sidebar Overlay */}
      <div 
        className={`sidebar-mobile-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Mobile Sidebar Drawer */}
      <div className={`sidebar-mobile ${sidebarOpen ? 'open' : ''}`}>
        <Sidebar 
          activeView={activeView} 
          setActiveView={(view) => {
            if (view !== 'messages') setChatUserId(null);
            setActiveView(view);
            setSidebarOpen(false);
          }}
          onCreatePost={() => {
            setShowCreatePost(true);
            setSidebarOpen(false);
          }}
          isMobile={true}
          onClose={() => setSidebarOpen(false)}
          networkRequestCount={networkRequestCount}
          tradeDealsCount={tradeDealsCount}
        />
      </div>

      {/* Desktop Sidebar */}
      <Sidebar 
        activeView={activeView} 
        setActiveView={(view) => {
          if (view !== 'messages') setChatUserId(null);
          setActiveView(view);
        }}
        onCreatePost={() => setShowCreatePost(true)}
        networkRequestCount={networkRequestCount}
        tradeDealsCount={tradeDealsCount}
      />
      
      <main className="main-feed">
        {activeView === 'feed' && (
          <Feed 
            posts={posts} 
            loading={postsLoading}
            onPostCreated={handlePostCreated}
            onCreatePost={() => setShowCreatePost(true)}
            onRefresh={fetchPosts}
            onViewProfile={handleViewProfile}
            onProposeTrade={handleProposeTrade}
            onStartChat={handleStartChat}
            onEditPost={handleEditPost}
          />
        )}
        {activeView === 'community' && (
          <CommunityBoard
            onViewProfile={handleViewProfile}
          />
        )}
        {activeView === 'trades' && <TradeDealsPanel />}
        {activeView === 'network' && (
          <TradeNetworkPanel 
            onViewProfile={handleViewProfile}
          />
        )}
        {activeView === 'messages' && (
          <MessagesPanel 
            initialChatUserId={chatUserId}
            key={chatUserId || 'messages'}
          />
        )}
        {activeView === 'invites' && <InvitePanel />}
        {activeView === 'profile' && <ProfilePanel />}
        {activeView === 'security' && <SecuritySettings />}
        {activeView === 'gallery' && viewingGallery && (
          <Gallery 
            userId={viewingGallery.userId}
            isOwnProfile={viewingGallery.userId === user?.id}
            onBack={() => {
              setViewingGallery(null);
              setActiveView('feed');
            }}
          />
        )}
        {activeView === 'my-gallery' && (
          <Gallery 
            userId={user?.id}
            isOwnProfile={true}
            onBack={() => setActiveView('profile')}
          />
        )}
        {activeView === 'admin' && user?.role === 'admin' && (
          <AdminDashboard 
            onBack={() => setActiveView('feed')} 
            onViewProfile={handleViewProfile}
          />
        )}
        {activeView === 'moderation' && user?.role === 'moderator' && (
          <ModerationDashboard
            onBack={() => setActiveView('feed')}
            onViewProfile={handleViewProfile}
          />
        )}
      </main>

      <RightPanel matches={matches} onViewProfile={handleViewProfile} />

      {/* Mobile Bottom Navigation */}
      <MobileNav 
        activeView={activeView}
        setActiveView={setActiveView}
        onCreatePost={() => setShowCreatePost(true)}
        networkRequestCount={networkRequestCount}
      />

      {showCreatePost && (
        <CreatePostModal 
          onClose={() => {
            setShowCreatePost(false);
            setEditingPost(null);
          }}
          onPostCreated={handlePostCreated}
          editPost={editingPost}
        />
      )}

      {viewingProfileId && (
        <UserProfileView
          userId={viewingProfileId}
          onClose={() => setViewingProfileId(null)}
          onStartChat={handleStartChat}
          onProposeTrade={handleProposeTrade}
          onViewGallery={handleViewGallery}
        />
      )}

      {tradeTarget && (
        <CreateTradeModal
          receiverId={tradeTarget.userId}
          receiverName={tradeTarget.userName}
          onClose={() => setTradeTarget(null)}
          onTradeCreated={() => {
            fetchTradeDealsCount();
          }}
        />
      )}

      {showOnboarding && (
        <OnboardingTour
          onComplete={() => {
            setShowOnboarding(false);
            updateUser({ has_seen_onboarding: true });
          }}
        />
      )}

      {currentAchievement && (
        <AchievementCelebration
          key={currentAchievement}
          achievementKey={currentAchievement}
          onAck={handleAckAchievement}
        />
      )}

      {/* One-time changelog — shown after onboarding & achievements */}
      {!showOnboarding && !currentAchievement && changelog && (
        <ChangelogModal
          changelog={changelog}
          onDismiss={() => setChangelog(null)}
        />
      )}
    </div>
  );
}
