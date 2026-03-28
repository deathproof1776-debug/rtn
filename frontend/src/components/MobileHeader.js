import { Shield, List, Plus } from '@phosphor-icons/react';
import NotificationBell from './NotificationBell';

export default function MobileHeader({ onMenuClick, onCreatePost }) {
  return (
    <header className="mobile-header" data-testid="mobile-header">
      <button 
        onClick={onMenuClick}
        className="p-2 -ml-2 text-[#A8A29E] hover:text-[#E7E5E4] transition-colors"
        data-testid="mobile-menu-button"
        aria-label="Open menu"
      >
        <List size={24} weight="bold" />
      </button>

      <div className="flex items-center gap-2">
        <Shield size={24} weight="duotone" className="text-[#B45309]" />
        <span 
          className="text-sm font-black tracking-tight text-[#E7E5E4]" 
          style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}
        >
          HOMESTEAD
        </span>
      </div>

      <div className="flex items-center gap-1">
        <NotificationBell />
        <button 
          onClick={onCreatePost}
          className="p-2 text-[#B45309] hover:text-[#92400E] transition-colors"
          data-testid="mobile-create-post"
          aria-label="Create post"
        >
          <Plus size={24} weight="bold" />
        </button>
      </div>
    </header>
  );
}
