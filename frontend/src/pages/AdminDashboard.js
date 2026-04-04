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
  Crown,
  ArrowLeft,
  Warning,
  Eye,
  ClockCounterClockwise,
  UserMinus,
  Notepad,
  Megaphone,
  Plus,
  PencilSimple,
  ToggleLeft,
  ToggleRight,
  UsersThree
} from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function StatCard({ icon: Icon, label, value, subValue, color }) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-3" data-testid={`stat-${label.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          <Icon size={16} style={{ color }} weight="duotone" />
        </div>
        <div>
          <p className="text-xl font-bold text-[var(--text-primary)]">{value}</p>
          <p className="text-[10px] text-[var(--text-muted)]">{label}</p>
        </div>
      </div>
      {subValue && (
        <p className="text-[9px] text-[var(--text-muted)] mt-1 pt-1 border-t border-[var(--border-color)]">{subValue}</p>
      )}
    </div>
  );
}

function QuickUserRow({ user, onVerify, onChangeRole, onDelete, onViewProfile, currentUserId }) {
  const [showActions, setShowActions] = useState(false);
  const isSelf = user._id === currentUserId;

  return (
    <div className="flex items-center gap-2 p-2 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] text-xs">
      <div className="w-7 h-7 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] text-xs font-bold flex-shrink-0">
        {user.name?.charAt(0)?.toUpperCase() || 'U'}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span className="font-medium text-[var(--text-primary)] truncate">{user.name}</span>
          {user.is_verified && <SealCheck size={12} className="text-[var(--brand-primary)]" weight="fill" />}
          {user.role === 'admin' && <Crown size={12} className="text-[var(--brand-accent)]" />}
        </div>
        <p className="text-[10px] text-[var(--text-muted)] truncate">{user.email}</p>
      </div>
      <div className="relative flex-shrink-0">
        <button onClick={() => setShowActions(!showActions)} className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]">
          <CaretDown size={14} />
        </button>
        {showActions && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setShowActions(false)} />
            <div className="absolute right-0 top-full mt-1 z-50 bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-lg min-w-[150px]">
              <button onClick={() => { onViewProfile?.(user._id); setShowActions(false); }} className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]">
                <Eye size={14} /> View Profile
              </button>
              <button onClick={() => { onVerify(user._id, !user.is_verified); setShowActions(false); }} className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]">
                <SealCheck size={14} /> {user.is_verified ? 'Unverify' : 'Verify'}
              </button>
              {!isSelf && (
                <>
                  <button onClick={() => { onChangeRole(user._id, user.role === 'admin' ? 'user' : 'admin'); setShowActions(false); }} className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-[var(--text-primary)]">
                    <Crown size={14} /> {user.role === 'admin' ? 'Demote' : 'Promote'}
                  </button>
                  <button onClick={() => { onDelete(user._id, user.name); setShowActions(false); }} className="w-full px-3 py-2 text-left text-xs flex items-center gap-2 hover:bg-[var(--bg-surface-hover)] text-red-400">
                    <Trash size={14} /> Delete
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

function CommunityPostRow({ post, onDelete }) {
  return (
    <div className="flex items-start gap-2 p-2 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] text-xs">
      <div className="w-6 h-6 bg-[var(--bg-surface-hover)] flex items-center justify-center text-[var(--brand-primary)] text-[10px] font-bold flex-shrink-0">
        {post.user_name?.charAt(0)?.toUpperCase() || 'U'}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1 flex-wrap">
          <span className="font-medium text-[var(--text-primary)]">{post.user_name}</span>
          {post.category && <span className="text-[9px] px-1 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)]">{post.category}</span>}
        </div>
        <p className="text-[var(--text-secondary)] line-clamp-1">{post.content || post.title}</p>
        <p className="text-[9px] text-[var(--text-muted)] mt-0.5">{new Date(post.created_at).toLocaleDateString()}</p>
      </div>
      <button onClick={() => onDelete(post._id, 'this community post')} className="p-1 text-[var(--text-muted)] hover:text-red-400 flex-shrink-0">
        <Trash size={14} />
      </button>
    </div>
  );
}

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
    await axios.post(`${API_URL}/api/admin/verify-trader`, { user_id: userId, is_verified: isVerified }, { withCredentials: true });
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
    ? users.filter(u => u.name?.toLowerCase().includes(searchQuery.toLowerCase()) || u.email?.toLowerCase().includes(searchQuery.toLowerCase()))
    : users;

  const getTimeAgo = (dateStr) => {
    const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
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

      {/* Stats Row */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-4">
        <StatCard icon={Users} label="Users" value={stats?.total_users || 0} subValue={`+${stats?.new_users_week || 0} this week`} color="var(--brand-primary)" />
        <StatCard icon={SealCheck} label="Verified" value={stats?.verified_users || 0} color="var(--brand-accent)" />
        <StatCard icon={Article} label="Posts" value={stats?.total_posts || 0} color="#0369A1" />
        <StatCard icon={ChatCircle} label="Messages" value={stats?.total_messages || 0} color="#7C3AED" />
        <StatCard icon={Handshake} label="Connections" value={stats?.total_connections || 0} color="#DC2626" />
        <StatCard icon={Envelope} label="Invites" value={stats?.total_invites || 0} subValue={`${stats?.used_invites || 0} used`} color="#059669" />
      </div>

      {/* Main Grid - All sections on one page */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* LEFT COLUMN: Users */}
        <div className="lg:col-span-1 space-y-4">
          {/* Users Section */}
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
              <Users size={16} className="text-[var(--brand-primary)]" />
              <span className="text-sm font-medium text-[var(--text-primary)]">Users</span>
              <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] ml-auto">{users.length}</span>
            </div>
            <div className="p-2 border-b border-[var(--border-color)]">
              <div className="relative">
                <MagnifyingGlass size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input-field w-full text-xs py-1.5 pl-7"
                  placeholder="Search users..."
                />
              </div>
            </div>
            <div className="max-h-[300px] overflow-y-auto">
              {filteredUsers.slice(0, 15).map(u => (
                <QuickUserRow
                  key={u._id}
                  user={u}
                  currentUserId={user?.id}
                  onVerify={handleVerify}
                  onChangeRole={handleChangeRole}
                  onDelete={(id, name) => handleDelete(id, `user "${name}"`, 'user')}
                  onViewProfile={onViewProfile}
                />
              ))}
            </div>
          </div>

          {/* Announcements Section */}
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
              <Megaphone size={16} className="text-[var(--brand-accent)]" />
              <span className="text-sm font-medium text-[var(--text-primary)]">Announcements</span>
              <button onClick={() => setShowCreateMessage(true)} className="ml-auto p-1 text-[var(--brand-primary)] hover:bg-[var(--bg-surface-hover)]">
                <Plus size={14} weight="bold" />
              </button>
            </div>
            <div className="max-h-[200px] overflow-y-auto">
              {systemMessages.length === 0 ? (
                <div className="py-6 text-center text-xs text-[var(--text-muted)]">No announcements</div>
              ) : (
                systemMessages.map(msg => (
                  <div key={msg._id} className="flex items-center gap-2 p-2 border-b border-[var(--border-color)] text-xs">
                    <span className={`w-2 h-2 rounded-full ${msg.is_active ? 'bg-green-500' : 'bg-gray-500'}`} />
                    <span className="flex-1 truncate text-[var(--text-primary)]">{msg.message}</span>
                    <button onClick={() => setEditingMessage(msg)} className="p-1 text-[var(--text-muted)] hover:text-[var(--brand-primary)]">
                      <PencilSimple size={12} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* MIDDLE COLUMN: Posts */}
        <div className="lg:col-span-1 space-y-4">
          {/* Barter Posts Section */}
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
              <Article size={16} className="text-blue-500" />
              <span className="text-sm font-medium text-[var(--text-primary)]">Barter Posts</span>
              <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] ml-auto">{posts.length}</span>
            </div>
            <div className="max-h-[250px] overflow-y-auto">
              {posts.slice(0, 10).map(p => (
                <div key={p._id} className="flex items-start gap-2 p-2 border-b border-[var(--border-color)] hover:bg-[var(--bg-surface-hover)] text-xs">
                  <div className="flex-1 min-w-0">
                    <span className="font-medium text-[var(--text-primary)] line-clamp-1">{p.title}</span>
                    <p className="text-[10px] text-[var(--text-muted)]">by {p.user_name}</p>
                  </div>
                  <button onClick={() => handleDelete(p._id, `post "${p.title}"`, 'post')} className="p-1 text-[var(--text-muted)] hover:text-red-400">
                    <Trash size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Community Feed Section */}
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
              <UsersThree size={16} className="text-purple-500" />
              <span className="text-sm font-medium text-[var(--text-primary)]">Community Feed</span>
              <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-surface-hover)] text-[var(--text-muted)] ml-auto">{communityPosts.length}</span>
            </div>
            <div className="max-h-[250px] overflow-y-auto">
              {communityPosts.length === 0 ? (
                <div className="py-6 text-center text-xs text-[var(--text-muted)]">No community posts</div>
              ) : (
                communityPosts.slice(0, 10).map(p => (
                  <CommunityPostRow key={p._id} post={p} onDelete={(id, label) => handleDelete(id, label, 'community')} />
                ))
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Activity Log */}
        <div className="lg:col-span-1">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)]">
            <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
              <ClockCounterClockwise size={16} className="text-[var(--text-muted)]" />
              <span className="text-sm font-medium text-[var(--text-primary)]">Activity Log</span>
            </div>
            <div className="max-h-[520px] overflow-y-auto">
              {auditLogs.length === 0 ? (
                <div className="py-8 text-center text-xs text-[var(--text-muted)]">No activity yet</div>
              ) : (
                auditLogs.map((log, idx) => {
                  const icons = {
                    verified: { icon: SealCheck, color: 'var(--brand-accent)' },
                    unverified: { icon: SealCheck, color: '#DC2626' },
                    role_changed: { icon: Crown, color: 'var(--brand-primary)' },
                    deleted_post: { icon: Trash, color: '#DC2626' },
                    deleted_user: { icon: UserMinus, color: '#DC2626' },
                  };
                  const config = icons[log.action] || { icon: Notepad, color: 'var(--text-muted)' };
                  const ActionIcon = config.icon;

                  return (
                    <div key={log._id || idx} className="flex items-start gap-2 px-3 py-2 border-b border-[var(--border-color)] text-xs">
                      <div className="w-6 h-6 flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${config.color}20` }}>
                        <ActionIcon size={12} style={{ color: config.color }} weight="fill" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[var(--text-primary)]">
                          <span className="font-medium">{log.admin_name}</span>
                          <span className="text-[var(--text-muted)]"> → </span>
                          <span className="font-medium">{log.target_name}</span>
                        </p>
                        <p className="text-[10px] text-[var(--text-muted)]">{log.action.replace('_', ' ')} • {getTimeAgo(log.created_at)}</p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Confirm Dialog */}
      {confirmAction && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 max-w-sm mx-4 w-full">
            <div className="flex items-center gap-2 mb-3">
              <Warning size={18} className="text-red-400" />
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">Confirm Action</h3>
            </div>
            <p className="text-xs text-[var(--text-secondary)] mb-4">{confirmAction.label}</p>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setConfirmAction(null)} className="btn-secondary px-3 py-1.5 text-xs">Cancel</button>
              <button onClick={executeConfirmAction} className="px-3 py-1.5 text-xs font-medium bg-red-600 hover:bg-red-700 text-white">Confirm</button>
            </div>
          </div>
        </div>
      )}

      {/* Announcement Modal */}
      {(showCreateMessage || editingMessage) && (
        <AnnouncementModal
          message={editingMessage}
          onClose={() => { setShowCreateMessage(false); setEditingMessage(null); }}
          onSave={async (data) => {
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
          }}
          onDelete={editingMessage ? async () => {
            await axios.delete(`${API_URL}/api/admin/system-messages/${editingMessage._id}`, { withCredentials: true });
            fetchAll();
            setEditingMessage(null);
          } : null}
          onToggle={editingMessage ? async () => {
            await axios.put(`${API_URL}/api/admin/system-messages/${editingMessage._id}`, { is_active: !editingMessage.is_active }, { withCredentials: true });
            fetchAll();
            setEditingMessage({ ...editingMessage, is_active: !editingMessage.is_active });
          } : null}
        />
      )}
    </div>
  );
}

function AnnouncementModal({ message, onClose, onSave, onDelete, onToggle }) {
  const [formData, setFormData] = useState({
    message: message?.message || '',
    type: message?.type || 'info',
    priority: message?.priority || 0,
    is_active: message?.is_active ?? true
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.message.trim()) return;
    setSaving(true);
    await onSave(formData);
    setSaving(false);
  };

  const typeColors = {
    info: 'border-blue-500 bg-blue-500/10',
    warning: 'border-yellow-500 bg-yellow-500/10',
    success: 'border-green-500 bg-green-500/10',
    urgent: 'border-red-500 bg-red-500/10'
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60">
      <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 max-w-md mx-4 w-full">
        <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">
          {message ? 'Edit Announcement' : 'New Announcement'}
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Message</label>
            <textarea
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="input-field w-full h-20 resize-none text-sm"
              placeholder="Enter announcement..."
              required
            />
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="input-field w-full text-sm"
              >
                <option value="info">Info</option>
                <option value="success">Success</option>
                <option value="warning">Warning</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Priority</label>
              <input
                type="number"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                className="input-field w-full text-sm"
                min="0" max="100"
              />
            </div>
          </div>

          {/* Preview */}
          <div className={`p-2 border-l-4 text-xs ${typeColors[formData.type]}`}>
            <p className="text-[var(--text-primary)]">{formData.message || 'Preview...'}</p>
          </div>
          
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4"
              />
              <label htmlFor="is_active" className="text-xs text-[var(--text-secondary)]">Active</label>
            </div>
            
            <div className="flex gap-2">
              {message && onDelete && (
                <button type="button" onClick={onDelete} className="text-xs text-red-400 hover:text-red-300 px-2">
                  Delete
                </button>
              )}
              <button type="button" onClick={onClose} className="btn-secondary px-3 py-1.5 text-xs">Cancel</button>
              <button type="submit" disabled={saving || !formData.message.trim()} className="btn-primary px-3 py-1.5 text-xs">
                {saving ? '...' : message ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
