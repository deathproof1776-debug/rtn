import { useState, useEffect } from 'react';
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
import UserProfileView from '../components/UserProfileView';
import MobileNav from '../components/MobileNav';
import MobileHeader from '../components/MobileHeader';
import InvitePanel from '../components/InvitePanel';

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
  const [viewingProfileId, setViewingProfileId] = useState(null);

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

  useEffect(() => {
    if (user) {
      fetchPosts();
      fetchMatches();
      fetchNetworkRequests();
    }
  }, [user]);

  const fetchPosts = async () => {
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
  };

  const fetchMatches = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/posts/matches`, {
        withCredentials: true
      });
      setMatches(response.data);
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  };

  const fetchNetworkRequests = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/network/requests/pending`, {
        withCredentials: true
      });
      setNetworkRequestCount(response.data.incoming_count || 0);
    } catch (error) {
      console.error('Error fetching network requests:', error);
    }
  };

  const handlePostCreated = (newPost) => {
    setPosts([newPost, ...posts]);
    setShowCreatePost(false);
  };

  const handleViewProfile = (userId) => {
    setViewingProfileId(userId);
  };

  const handleStartChat = (userId) => {
    setViewingProfileId(null);
    setActiveView('messages');
    // The MessagesPanel will need to handle starting a chat with this user
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0C0A09] flex items-center justify-center">
        <div className="text-[#A8A29E]">Loading...</div>
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
        />
      </div>

      {/* Desktop Sidebar */}
      <Sidebar 
        activeView={activeView} 
        setActiveView={setActiveView}
        onCreatePost={() => setShowCreatePost(true)}
        networkRequestCount={networkRequestCount}
      />
      
      <main className="main-feed">
        {activeView === 'feed' && (
          <Feed 
            posts={posts} 
            loading={postsLoading}
            onPostCreated={handlePostCreated}
            onCreatePost={() => setShowCreatePost(true)}
            onRefresh={fetchPosts}
          />
        )}
        {activeView === 'network' && (
          <TradeNetworkPanel 
            onViewProfile={handleViewProfile}
          />
        )}
        {activeView === 'messages' && <MessagesPanel />}
        {activeView === 'invites' && <InvitePanel />}
        {activeView === 'profile' && <ProfilePanel />}
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
        />
      )}
    </div>
  );
}
