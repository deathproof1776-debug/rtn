import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
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

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Dashboard() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [activeView, setActiveView] = useState('feed');
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

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

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
    setPosts([newPost, ...posts]);
    setShowCreatePost(false);
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
    <div className="app-shell" data-testid="dashboard">
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
          <AdminDashboard onBack={() => setActiveView('feed')} />
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
          onClose={() => setShowCreatePost(false)}
          onPostCreated={handlePostCreated}
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
    </div>
  );
}
