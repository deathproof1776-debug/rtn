import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { ShieldCheck, ArrowLeft } from '@phosphor-icons/react';
import StatsBar from '../components/admin/StatsBar';
import AnnouncementsSection from '../components/admin/AnnouncementsSection';
import AnnouncementModal from '../components/admin/AnnouncementModal';
import UsersPanel from '../components/admin/UsersPanel';
import PostsPanel from '../components/admin/PostsPanel';
import CommunityPanel from '../components/admin/CommunityPanel';
import ActivityLogPanel from '../components/admin/ActivityLogPanel';
import ConfirmDialog from '../components/admin/ConfirmDialog';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AdminDashboard({ onBack, onViewProfile }) {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [communityPosts, setCommunityPosts] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [systemMessages, setSystemMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [confirmAction, setConfirmAction] = useState(null);
  const [showCreateMessage, setShowCreateMessage] = useState(false);
  const [editingMessage, setEditingMessage] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      const [statsRes, usersRes, postsRes, communityRes, logsRes, msgRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/stats`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/users?limit=50`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/posts?limit=20`, { withCredentials: true }),
        axios.get(`${API_URL}/api/community?limit=20`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/audit-log?limit=10`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/system-messages`, { withCredentials: true })
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data.users || []);
      setPosts(postsRes.data.posts || []);
      setCommunityPosts(communityRes.data || []);
      setAuditLogs(logsRes.data.logs || []);
      setSystemMessages(msgRes.data.messages || []);
    } catch (err) {
      console.error('Error fetching admin data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleVerify = async (userId, isVerified) => {
    await axios.post(
      `${API_URL}/api/admin/verify-trader`,
      { user_id: userId, is_verified: isVerified },
      { withCredentials: true }
    );
    setUsers(users.map(u => u._id === userId ? { ...u, is_verified: isVerified } : u));
  };

  const handleChangeRole = async (userId, role) => {
    await axios.put(`${API_URL}/api/admin/users/${userId}/role`, { role }, { withCredentials: true });
    setUsers(users.map(u => u._id === userId ? { ...u, role } : u));
  };

  const handleDelete = (id, label, type) => {
    setConfirmAction({ type, id, label: `Delete ${label}? This cannot be undone.` });
  };

  const executeConfirmAction = async () => {
    if (!confirmAction) return;
    try {
      if (confirmAction.type === 'user') {
        await axios.delete(`${API_URL}/api/admin/users/${confirmAction.id}`, { withCredentials: true });
        setUsers(users.filter(u => u._id !== confirmAction.id));
      } else if (confirmAction.type === 'post') {
        await axios.delete(`${API_URL}/api/admin/posts/${confirmAction.id}`, { withCredentials: true });
        setPosts(posts.filter(p => p._id !== confirmAction.id));
      } else if (confirmAction.type === 'community') {
        await axios.delete(`${API_URL}/api/community/${confirmAction.id}`, { withCredentials: true });
        setCommunityPosts(communityPosts.filter(p => p._id !== confirmAction.id));
      }
      fetchAll();
    } catch (err) {
      console.error('Error:', err);
    }
    setConfirmAction(null);
  };

  const filteredUsers = searchQuery
    ? users.filter(u =>
        u.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.email?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : users;

  const handleSaveAnnouncement = async (data) => {
    try {
      if (editingMessage) {
        await axios.put(`${API_URL}/api/admin/system-messages/${editingMessage._id}`, data, { withCredentials: true });
      } else {
        await axios.post(`${API_URL}/api/admin/system-messages`, data, { withCredentials: true });
      }
      fetchAll();
      setShowCreateMessage(false);
      setEditingMessage(null);
    } catch (err) {
      console.error('Error saving announcement:', err);
    }
  };

  const handleDeleteAnnouncement = async () => {
    await axios.delete(`${API_URL}/api/admin/system-messages/${editingMessage._id}`, { withCredentials: true });
    fetchAll();
    setEditingMessage(null);
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-4 text-center">
        <div className="w-8 h-8 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto" data-testid="admin-dashboard">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <button onClick={onBack} className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)]">
          <ArrowLeft size={20} />
        </button>
        <ShieldCheck size={24} weight="duotone" className="text-[var(--brand-primary)]" />
        <h2 className="text-xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Admin Dashboard
        </h2>
      </div>

      <StatsBar stats={stats} />

      <AnnouncementsSection
        messages={systemMessages}
        onNew={() => setShowCreateMessage(true)}
        onEdit={setEditingMessage}
      />

      {/* Main Grid - All sections on one page */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1 space-y-4">
          <UsersPanel
            users={users}
            filteredUsers={filteredUsers}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            currentUserId={user?.id}
            onVerify={handleVerify}
            onChangeRole={handleChangeRole}
            onDelete={handleDelete}
            onViewProfile={onViewProfile}
          />
        </div>

        <div className="lg:col-span-1 space-y-4">
          <PostsPanel posts={posts} onDelete={handleDelete} />
          <CommunityPanel communityPosts={communityPosts} onDelete={handleDelete} />
        </div>

        <div className="lg:col-span-1">
          <ActivityLogPanel auditLogs={auditLogs} />
        </div>
      </div>

      <ConfirmDialog
        action={confirmAction}
        onCancel={() => setConfirmAction(null)}
        onConfirm={executeConfirmAction}
      />

      {(showCreateMessage || editingMessage) && (
        <AnnouncementModal
          message={editingMessage}
          onClose={() => { setShowCreateMessage(false); setEditingMessage(null); }}
          onSave={handleSaveAnnouncement}
          onDelete={editingMessage ? handleDeleteAnnouncement : null}
        />
      )}
    </div>
  );
}
