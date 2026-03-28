import { Shield, List, Plus } from '@phosphor-icons/react';
import NotificationBell from './NotificationBell';
import ThemeToggle from './ThemeToggle';

export default function MobileHeader({ onMenuClick, onCreatePost }) {
  return (
    <header className="mobile-header" data-testid="mobile-header">
      <button 
        onClick={onMenuClick}
        className="p-2 -ml-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
        data-testid="mobile-menu-button"
        aria-label="Open menu"
      >
        <List size={24} weight="bold" />
      </button>

      <div className="flex items-center gap-2">
        <Shield size={24} weight="duotone" className="text-[var(--brand-primary)]" />
        <span 
          className="text-sm font-black tracking-tight text-[var(--text-primary)]" 
          style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}
        >
          REBEL TRADE NETWORK
        </span>
      </div>

      <div className="flex items-center gap-1">
        <ThemeToggle />
        <NotificationBell />
        <button 
          onClick={onCreatePost}
          className="p-2 text-[var(--brand-primary)] hover:text-[var(--brand-primary-hover)] transition-colors"
          data-testid="mobile-create-post"
          aria-label="Create post"
        >
          <Plus size={24} weight="bold" />
        </button>
      </div>
    </header>
  );
}
