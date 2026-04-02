import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import {
  ShieldCheck,
  Users,
  Article,
  ChatCircle,
  Handshake,
  Envelope,
  SealCheck,
  Trash,
  CaretDown,
  CaretUp,
  MagnifyingGlass,
  ChartBar,
  UserCircle,
  Crown,
  ArrowLeft,
  Warning,
  Eye,
  ClockCounterClockwise,
  UserMinus,
  Notepad
} from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function StatCard({ icon: Icon, label, value, subValue, color }) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4" data-testid={`stat-${label.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          <Icon size={20} style={{ color }} weight="duotone" />
        </div>
        <div>
          <p className="text-2xl font-bold text-[var(--text-primary)]">{value}</p>
          <p className="text-xs text-[var(--text-muted)]">{label}</p>
        </div>
      </div>
      {subValue && (
        <p className="text-[10px] text-[var(--text-muted)] mt-2 border-t border-[var(--border-color)] pt-2">{subValue}</p>
      )}
    </div>
  );
}

function UserRow({ user, onVerify, onChangeRole, onDelete, currentUserId }) {
  const [showActions, setShowActions] = useState(false);
  const isSelf = user._id === currentUserId;

  return (
    <div className="flex items-center gap-3 p-3 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] transition-colors" data-testid={`admin-user-row-${user._id}`}>
      <div className="w-9 h-9 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] text-sm font-bold flex-shrink-0">
        {user.avatar ? (
          <img src={user.avatar} alt="" className="w-full h-full object-cover" />
        ) : (
          user.name?.charAt(0)?.toUpperCase() || 'U'
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-sm font-medium text-[var(--text-primary)] truncate">{user.name}</span>
          {user.is_verified && <SealCheck size={14} className="text-[var(--brand-primary)]" weight="fill" />}
          {user.role === 'admin' && (
            <span className="text-[9px] px-1.5 py-0.5 bg-[var(--brand-primary)]/20 text-[var(--brand-primary)] font-semibold uppercase tracking-wider">Admin</span>
          )}
          {isSelf && (
            <span className="text-[9px] px-1.5 py-0.5 bg-[#4D7C0F]/20 text-[#4D7C0F] font-semibold uppercase tracking-wider">You</span>
          )}
        </div>
        <p className="text-xs text-[var(--text-muted)] truncate">{user.email}</p>
        {user.location && <p className="text-[10px] text-[var(--text-muted)]">{user.location}</p>}
      </div>
      <div className="relative flex-shrink-0">
        <button
          onClick={() => setShowActions(!showActions)}
          className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-active)] transition-colors"
          data-testid={`admin-user-actions-${user._id}`}
        >
          {showActions ? <CaretUp size={16} /> : <CaretDown size={16} />}
        </button>
        {showActions && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setShowActions(false)} />
            <div className="absolute right-0 top-full mt-1 z-50 bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-lg min-w-[180px]" data-testid={`admin-user-menu-${user._id}`}>
              <button
                onClick={() => { onVerify(user._id, !user.is_verified); setShowActions(false); }}
                className="w-full px-3 py-2 text-left text-sm flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
                data-testid={`admin-verify-${user._id}`}
              >
                <SealCheck size={16} />
                {user.is_verified ? 'Remove Verification' : 'Verify Trader'}
              </button>
              {!isSelf && (
                <>
                  <button
                    onClick={() => { onChangeRole(user._id, user.role === 'admin' ? 'user' : 'admin'); setShowActions(false); }}
                    className="w-full px-3 py-2 text-left text-sm flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]"
                    data-testid={`admin-role-${user._id}`}
                  >
                    <Crown size={16} />
                    {user.role === 'admin' ? 'Demote to User' : 'Promote to Admin'}
                  </button>
                  <button
                    onClick={() => { onDelete(user._id, user.name); setShowActions(false); }}
                    className="w-full px-3 py-2 text-left text-sm flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-red-400"
                    data-testid={`admin-delete-${user._id}`}
                  >
                    <Trash size={16} />
                    Delete User
                  </button>
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function PostRow({ post, onDelete }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="p-3 border-b border-[var(--border-color)]" data-testid={`admin-post-row-${post._id}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-[var(--text-primary)]">{post.title}</span>
            <span className="text-[9px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] uppercase">{post.category}</span>
          </div>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">by {post.user_name} &middot; {new Date(post.created_at).toLocaleDateString()}</p>
          {expanded && (
            <p className="text-sm text-[var(--text-secondary)] mt-2">{post.description}</p>
          )}
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-active)] transition-colors"
          >
            <Eye size={16} />
          </button>
          <button
            onClick={() => onDelete(post._id, post.title)}
            className="p-1.5 text-[var(--text-muted)] hover:text-red-400 hover:bg-[var(--bg-surface-active)] transition-colors"
            data-testid={`admin-delete-post-${post._id}`}
          >
            <Trash size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AdminDashboard({ onBack }) {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditTotal, setAuditTotal] = useState(0);
  const [usersTotal, setUsersTotal] = useState(0);
  const [postsTotal, setPostsTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [confirmAction, setConfirmAction] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/admin/stats`, { withCredentials: true });
      setStats(res.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/admin/users?limit=100`, { withCredentials: true });
      setUsers(res.data.users || []);
      setUsersTotal(res.data.total || 0);
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  }, []);

  const fetchPosts = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/admin/posts?limit=100`, { withCredentials: true });
      setPosts(res.data.posts || []);
      setPostsTotal(res.data.total || 0);
    } catch (err) {
      console.error('Error fetching posts:', err);
    }
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/admin/audit-log?limit=100`, { withCredentials: true });
      setAuditLogs(res.data.logs || []);
      setAuditTotal(res.data.total || 0);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    fetchUsers();
    fetchPosts();
    fetchAuditLogs();
  }, [fetchStats, fetchUsers, fetchPosts, fetchAuditLogs]);

  const handleVerify = async (userId, isVerified) => {
    try {
      await axios.post(`${API_URL}/api/admin/verify-trader`, { user_id: userId, is_verified: isVerified }, { withCredentials: true });
      setUsers(users.map(u => u._id === userId ? { ...u, is_verified: isVerified } : u));
      fetchAuditLogs();
    } catch (err) {
      console.error('Error updating verification:', err);
    }
  };

  const handleChangeRole = async (userId, role) => {
    try {
      await axios.put(`${API_URL}/api/admin/users/${userId}/role`, { role }, { withCredentials: true });
      setUsers(users.map(u => u._id === userId ? { ...u, role } : u));
      fetchAuditLogs();
    } catch (err) {
      console.error('Error updating role:', err);
    }
  };

  const handleDeleteUser = (userId, userName) => {
    setConfirmAction({
      type: 'deleteUser',
      id: userId,
      label: `Delete user "${userName}"? This will remove all their posts, messages, and connections.`,
    });
  };

  const handleDeletePost = (postId, postTitle) => {
    setConfirmAction({
      type: 'deletePost',
      id: postId,
      label: `Delete post "${postTitle}"?`,
    });
  };

  const executeConfirmAction = async () => {
    if (!confirmAction) return;
    try {
      if (confirmAction.type === 'deleteUser') {
        await axios.delete(`${API_URL}/api/admin/users/${confirmAction.id}`, { withCredentials: true });
        setUsers(users.filter(u => u._id !== confirmAction.id));
        fetchStats();
        fetchAuditLogs();
      } else if (confirmAction.type === 'deletePost') {
        await axios.delete(`${API_URL}/api/admin/posts/${confirmAction.id}`, { withCredentials: true });
        setPosts(posts.filter(p => p._id !== confirmAction.id));
        fetchStats();
        fetchAuditLogs();
      }
    } catch (err) {
      console.error('Error executing action:', err);
    }
    setConfirmAction(null);
  };

  const filteredUsers = searchQuery
    ? users.filter(u => u.name?.toLowerCase().includes(searchQuery.toLowerCase()) || u.email?.toLowerCase().includes(searchQuery.toLowerCase()))
    : users;

  const getTimeAgo = (dateStr) => {
    const now = new Date();
    const date = new Date(dateStr);
    const seconds = Math.floor((now - date) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: ChartBar },
    { id: 'users', label: 'Users', icon: Users, count: usersTotal },
    { id: 'posts', label: 'Posts', icon: Article, count: postsTotal },
    { id: 'activity', label: 'Activity Log', icon: ClockCounterClockwise, count: auditTotal },
  ];

  return (
    <div className="max-w-3xl mx-auto" data-testid="admin-dashboard">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <button
          onClick={onBack}
          className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
          data-testid="admin-back-button"
        >
          <ArrowLeft size={20} />
        </button>
        <ShieldCheck size={24} weight="duotone" className="text-[var(--brand-primary)]" />
        <h2 className="text-xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Admin Dashboard
        </h2>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-5 border-b border-[var(--border-color)]">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab.id
                ? 'border-[var(--brand-primary)] text-[var(--brand-primary)]'
                : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
            data-testid={`admin-tab-${tab.id}`}
          >
            <tab.icon size={18} />
            {tab.label}
            {tab.count !== undefined && (
              <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] rounded-full">{tab.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-4" data-testid="admin-overview">
          {loading ? (
            <div className="text-center py-8 text-[var(--text-muted)]">Loading stats...</div>
          ) : stats ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                <StatCard icon={Users} label="Total Users" value={stats.total_users} subValue={`+${stats.new_users_week} this week`} color="#B45309" />
                <StatCard icon={SealCheck} label="Verified Traders" value={stats.verified_users} color="#4D7C0F" />
                <StatCard icon={Article} label="Total Posts" value={stats.total_posts} subValue={`+${stats.new_posts_week} this week`} color="#0369A1" />
                <StatCard icon={ChatCircle} label="Messages" value={stats.total_messages} color="#7C3AED" />
                <StatCard icon={Handshake} label="Connections" value={stats.total_connections} subValue={`${stats.pending_requests} pending requests`} color="#DC2626" />
                <StatCard icon={Envelope} label="Invites" value={stats.total_invites} subValue={`${stats.used_invites} used`} color="#059669" />
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-[var(--text-muted)]">Failed to load stats</div>
          )}
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div data-testid="admin-users-tab">
          <div className="relative mb-3">
            <MagnifyingGlass size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field w-full"
              style={{ paddingLeft: '2.25rem' }}
              placeholder="Search users by name or email..."
              data-testid="admin-user-search"
            />
          </div>
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center justify-between">
              <span className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">
                {filteredUsers.length} {filteredUsers.length === 1 ? 'user' : 'users'}
              </span>
            </div>
            <div className="max-h-[60vh] overflow-y-auto">
              {filteredUsers.map(u => (
                <UserRow
                  key={u._id}
                  user={u}
                  currentUserId={user?.id}
                  onVerify={handleVerify}
                  onChangeRole={handleChangeRole}
                  onDelete={handleDeleteUser}
                />
              ))}
              {filteredUsers.length === 0 && (
                <div className="py-8 text-center text-[var(--text-muted)] text-sm">No users found</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Posts Tab */}
      {activeTab === 'posts' && (
        <div data-testid="admin-posts-tab">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)]">
              <span className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">{postsTotal} posts</span>
            </div>
            <div className="max-h-[60vh] overflow-y-auto">
              {posts.map(p => (
                <PostRow key={p._id} post={p} onDelete={handleDeletePost} />
              ))}
              {posts.length === 0 && (
                <div className="py-8 text-center text-[var(--text-muted)] text-sm">No posts found</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Activity Log Tab */}
      {activeTab === 'activity' && (
        <div data-testid="admin-activity-tab">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)]">
              <span className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">{auditTotal} actions logged</span>
            </div>
            <div className="max-h-[60vh] overflow-y-auto">
              {auditLogs.length === 0 ? (
                <div className="py-12 text-center">
                  <ClockCounterClockwise size={32} className="text-[var(--text-muted)] mx-auto mb-2" />
                  <p className="text-sm text-[var(--text-muted)]">No admin actions recorded yet.</p>
                  <p className="text-xs text-[var(--text-muted)] mt-1">Actions like verifying traders, changing roles, and deleting content will appear here.</p>
                </div>
              ) : (
                auditLogs.map((log, idx) => {
                  const actionConfig = {
                    verified: { icon: SealCheck, color: '#4D7C0F', label: 'Verified trader' },
                    unverified: { icon: SealCheck, color: '#DC2626', label: 'Removed verification from' },
                    role_changed: { icon: Crown, color: '#B45309', label: 'Changed role of' },
                    deleted_post: { icon: Trash, color: '#DC2626', label: 'Deleted post' },
                    deleted_user: { icon: UserMinus, color: '#DC2626', label: 'Deleted user' },
                  };
                  const config = actionConfig[log.action] || { icon: Notepad, color: '#78716C', label: log.action };
                  const ActionIcon = config.icon;
                  const timeAgo = getTimeAgo(log.created_at);

                  return (
                    <div key={idx} className="flex items-start gap-3 px-4 py-3 border-b border-[var(--border-color)] last:border-b-0" data-testid={`audit-log-entry-${idx}`}>
                      <div className="w-8 h-8 flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: `${config.color}20` }}>
                        <ActionIcon size={16} style={{ color: config.color }} weight="fill" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-[var(--text-primary)]">
                          <span className="font-medium">{log.admin_name}</span>
                          {' '}<span className="text-[var(--text-secondary)]">{config.label}</span>{' '}
                          <span className="font-medium">{log.target_name}</span>
                        </p>
                        {log.details && (
                          <p className="text-xs text-[var(--text-muted)] mt-0.5">{log.details}</p>
                        )}
                        <p className="text-[10px] text-[var(--text-muted)] mt-1">{timeAgo}</p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

      {/* Confirm Dialog */}
      {confirmAction && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60" data-testid="admin-confirm-dialog">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-5 max-w-sm mx-4 w-full">
            <div className="flex items-center gap-2 mb-3">
              <Warning size={20} className="text-red-400" />
              <h3 className="text-base font-semibold text-[var(--text-primary)]">Confirm Action</h3>
            </div>
            <p className="text-sm text-[var(--text-secondary)] mb-4">{confirmAction.label}</p>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setConfirmAction(null)}
                className="btn-secondary px-4 py-2 text-sm"
                data-testid="admin-confirm-cancel"
              >
                Cancel
              </button>
              <button
                onClick={executeConfirmAction}
                className="px-4 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white transition-colors"
                data-testid="admin-confirm-execute"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
