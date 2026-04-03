import { House, ChatCircle, User, Plus, Handshake } from '@phosphor-icons/react';

export default function MobileNav({ activeView, setActiveView, onCreatePost, networkRequestCount = 0 }) {
  const navItems = [
    { id: 'feed', label: 'Feed', icon: House },
    { id: 'network', label: 'Network', icon: Handshake, badge: networkRequestCount },
    { id: 'create', label: 'Post', icon: Plus, action: onCreatePost },
    { id: 'messages', label: 'Messages', icon: ChatCircle },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <nav className="mobile-nav" data-testid="mobile-nav">
      {navItems.map((item) => {
        const isActive = item.id === activeView;
        const isCreate = item.id === 'create';
        
        return (
          <button
            key={item.id}
            onClick={() => {
              if (item.action) {
                item.action();
              } else {
                setActiveView(item.id);
              }
            }}
            className={`mobile-nav-item ${isActive ? 'active' : ''}`}
            data-testid={`mobile-nav-${item.id}`}
            aria-label={item.label}
          >
            {isCreate ? (
              <div className="w-10 h-10 rounded-full bg-[var(--brand-primary)] flex items-center justify-center -mt-4 shadow-lg">
                <item.icon size={22} weight="bold" className="text-white" />
              </div>
            ) : (
              <div className="relative">
                <item.icon 
                  size={22} 
                  weight={isActive ? 'fill' : 'regular'} 
                />
                {item.badge > 0 && (
                  <span className="absolute -top-1 -right-1 bg-[var(--brand-primary)] text-white text-[9px] px-1 py-0.5 rounded-full min-w-[14px] text-center leading-none">
                    {item.badge}
                  </span>
                )}
              </div>
            )}
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
