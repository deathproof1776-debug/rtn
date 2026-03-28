import { House, ChatCircle, User, Plus } from '@phosphor-icons/react';

export default function MobileNav({ activeView, setActiveView, onCreatePost }) {
  const navItems = [
    { id: 'feed', label: 'Feed', icon: House },
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
              <div className="w-10 h-10 rounded-full bg-[#B45309] flex items-center justify-center -mt-4 shadow-lg">
                <item.icon size={22} weight="bold" className="text-white" />
              </div>
            ) : (
              <item.icon 
                size={22} 
                weight={isActive ? 'fill' : 'regular'} 
              />
            )}
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
