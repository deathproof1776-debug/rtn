import { useAuth } from '../contexts/AuthContext';
import { 
  House, 
  ChatCircle, 
  User, 
  Plus, 
  SignOut, 
  Shield,
  X
} from '@phosphor-icons/react';
import NotificationBell from './NotificationBell';

export default function Sidebar({ activeView, setActiveView, onCreatePost, isMobile = false, onClose }) {
  const { user, logout } = useAuth();

  const navItems = [
    { id: 'feed', label: 'Feed', icon: House },
    { id: 'messages', label: 'Messages', icon: ChatCircle },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  const handleLogout = async () => {
    await logout();
  };

  return (
    <aside className={isMobile ? '' : 'sidebar'} data-testid="sidebar">
      <div className="p-6 border-b border-[#292524]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield size={32} weight="duotone" className="text-[#B45309]" />
            <div>
              <h1 className="text-lg font-black tracking-tight text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                HOMESTEAD
              </h1>
              <p className="text-[10px] uppercase tracking-[0.15em] text-[#78716C]">Barter Network</p>
            </div>
          </div>
          {isMobile ? (
            <button 
              onClick={onClose}
              className="p-2 text-[#78716C] hover:text-[#E7E5E4] transition-colors"
              aria-label="Close menu"
            >
              <X size={24} weight="bold" />
            </button>
          ) : (
            <NotificationBell />
          )}
        </div>
      </div>

      <nav className="flex-1 py-4">
        <button
          onClick={onCreatePost}
          className="w-full mx-4 mb-4 btn-primary flex items-center justify-center gap-2"
          style={{ width: 'calc(100% - 2rem)' }}
          data-testid="create-post-button"
        >
          <Plus size={20} weight="bold" />
          New Barter Post
        </button>

        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`nav-link w-full ${activeView === item.id ? 'active' : ''}`}
            data-testid={`nav-${item.id}`}
          >
            <item.icon size={22} weight={activeView === item.id ? 'fill' : 'regular'} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-[#292524]">
        <div className="flex items-center gap-3 mb-4 px-2">
          <div className="w-10 h-10 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold">
            {user?.name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-[#E7E5E4] truncate">{user?.name || 'User'}</p>
            <p className="text-xs text-[#78716C] truncate">{user?.location || 'Location not set'}</p>
          </div>
        </div>
        
        <button
          onClick={handleLogout}
          className="nav-link w-full text-[#991B1B] hover:bg-[#991B1B]/10"
          data-testid="logout-button"
        >
          <SignOut size={20} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
