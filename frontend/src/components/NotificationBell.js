import { useState } from 'react';
import { Bell, BellRinging, BellSlash, Check, X } from '@phosphor-icons/react';
import { useNotifications } from '../contexts/NotificationContext';
import { toast } from 'sonner';

export default function NotificationBell() {
  const { 
    isSupported, 
    permission, 
    isSubscribed, 
    loading, 
    subscribe, 
    unsubscribe,
    sendTestNotification 
  } = useNotifications();
  
  const [showDropdown, setShowDropdown] = useState(false);

  const handleToggle = async () => {
    console.log('[NotificationBell] Toggle clicked, isSubscribed:', isSubscribed);
    
    if (isSubscribed) {
      const result = await unsubscribe();
      if (result.success) {
        toast.success('Notifications disabled');
      } else {
        toast.error('Failed to disable notifications: ' + result.error);
      }
    } else {
      console.log('[NotificationBell] Attempting to subscribe...');
      const result = await subscribe();
      console.log('[NotificationBell] Subscribe result:', result);
      
      if (result.success) {
        toast.success('Notifications enabled! You\'ll be alerted for messages, comments, and likes.');
      } else if (result.error === 'Permission denied') {
        toast.error('Please allow notifications in your browser settings');
      } else if (result.error?.includes('Service Worker')) {
        toast.error('Service Worker not ready. Please refresh the page and try again.');
      } else {
        toast.error('Failed to enable notifications: ' + (result.error || 'Unknown error'));
      }
    }
    setShowDropdown(false);
  };

  const handleTest = async () => {
    const result = await sendTestNotification();
    if (result.success) {
      toast.success('Test notification sent!');
    } else {
      toast.error('Failed to send test notification');
    }
    setShowDropdown(false);
  };

  if (!isSupported) {
    return (
      <div className="relative">
        <button
          className="p-2 rounded-lg text-[var(--text-muted)] cursor-not-allowed"
          title="Push notifications not supported in this browser"
          disabled
          data-testid="notification-bell-unsupported"
        >
          <BellSlash size={22} weight="bold" />
        </button>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className={`p-2 rounded-lg transition-all duration-200 ${
          isSubscribed 
            ? 'text-[var(--brand-primary)] hover:bg-[var(--brand-primary)]/10' 
            : 'text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] hover:text-[var(--text-primary)]'
        }`}
        data-testid="notification-bell"
        title={isSubscribed ? 'Notifications enabled' : 'Enable notifications'}
      >
        {loading ? (
          <div className="w-[22px] h-[22px] border-2 border-[var(--brand-primary)]/30 border-t-[var(--brand-primary)] rounded-full animate-spin" />
        ) : isSubscribed ? (
          <BellRinging size={22} weight="fill" className="animate-pulse" />
        ) : (
          <Bell size={22} weight="bold" />
        )}
      </button>

      {showDropdown && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setShowDropdown(false)}
          />
          <div 
            className="absolute right-0 mt-2 w-72 bg-[var(--bg-surface)] border border-[var(--border-color)] rounded-xl shadow-2xl z-50 overflow-hidden"
            data-testid="notification-dropdown"
          >
            <div className="p-4 border-b border-[var(--border-color)]">
              <h3 className="text-[var(--text-primary)] font-semibold flex items-center gap-2">
                <Bell size={18} weight="bold" className="text-[var(--brand-primary)]" />
                Push Notifications
              </h3>
              <p className="text-[var(--text-muted)] text-sm mt-1">
                Get alerts for messages, comments, matches & likes
              </p>
            </div>

            <div className="p-3 space-y-2">
              {permission === 'denied' ? (
                <div className="p-3 bg-[var(--brand-danger)]/10 border border-[var(--brand-danger)]/20 rounded-lg">
                  <p className="text-[var(--brand-danger)] text-sm">
                    Notifications are blocked. Please enable them in your browser settings.
                  </p>
                </div>
              ) : (
                <>
                  <button
                    onClick={handleToggle}
                    disabled={loading}
                    className={`w-full flex items-center justify-between p-3 rounded-lg transition-all ${
                      isSubscribed
                        ? 'bg-[var(--brand-primary)]/10 border border-[var(--brand-primary)]/30 text-[var(--brand-primary)] hover:bg-[var(--brand-primary)]/20'
                        : 'bg-[var(--bg-surface-hover)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-active)]'
                    }`}
                    data-testid="notification-toggle"
                  >
                    <span className="flex items-center gap-2">
                      {isSubscribed ? (
                        <>
                          <Check size={18} weight="bold" className="text-[var(--brand-success)]" />
                          Notifications On
                        </>
                      ) : (
                        <>
                          <X size={18} weight="bold" className="text-[var(--text-muted)]" />
                          Notifications Off
                        </>
                      )}
                    </span>
                    <span className="text-xs uppercase tracking-wide opacity-60">
                      {isSubscribed ? 'Click to disable' : 'Click to enable'}
                    </span>
                  </button>

                  {isSubscribed && (
                    <button
                      onClick={handleTest}
                      disabled={loading}
                      className="w-full p-3 bg-[var(--bg-surface-hover)] border border-[var(--border-color)] rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-surface-active)] hover:text-[var(--text-primary)] transition-all text-sm"
                      data-testid="notification-test"
                    >
                      Send Test Notification
                    </button>
                  )}
                </>
              )}
            </div>

            <div className="px-4 py-3 bg-[var(--bg-surface-hover)]/50 border-t border-[var(--border-color)]">
              <p className="text-[var(--text-muted)] text-xs">
                You'll receive notifications even when the app is closed
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
