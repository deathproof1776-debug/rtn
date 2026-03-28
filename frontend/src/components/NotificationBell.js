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
    if (isSubscribed) {
      const result = await unsubscribe();
      if (result.success) {
        toast.success('Notifications disabled');
      } else {
        toast.error('Failed to disable notifications: ' + result.error);
      }
    } else {
      const result = await subscribe();
      if (result.success) {
        toast.success('Notifications enabled! You\'ll be alerted for messages, comments, and likes.');
      } else if (result.error === 'Permission denied') {
        toast.error('Please allow notifications in your browser settings');
      } else {
        toast.error('Failed to enable notifications: ' + result.error);
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
          className="p-2 rounded-lg text-stone-500 cursor-not-allowed"
          title="Push notifications not supported in this browser"
          disabled
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
            ? 'text-amber-500 hover:bg-amber-500/10' 
            : 'text-stone-400 hover:bg-stone-800 hover:text-stone-200'
        }`}
        data-testid="notification-bell"
        title={isSubscribed ? 'Notifications enabled' : 'Enable notifications'}
      >
        {loading ? (
          <div className="w-[22px] h-[22px] border-2 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
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
            className="absolute right-0 mt-2 w-72 bg-stone-900 border border-stone-700 rounded-xl shadow-2xl z-50 overflow-hidden"
            data-testid="notification-dropdown"
          >
            <div className="p-4 border-b border-stone-700">
              <h3 className="text-stone-200 font-semibold flex items-center gap-2">
                <Bell size={18} weight="bold" className="text-amber-500" />
                Push Notifications
              </h3>
              <p className="text-stone-500 text-sm mt-1">
                Get alerts for messages, comments, matches & likes
              </p>
            </div>

            <div className="p-3 space-y-2">
              {permission === 'denied' ? (
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                  <p className="text-red-400 text-sm">
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
                        ? 'bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20'
                        : 'bg-stone-800 border border-stone-700 text-stone-300 hover:bg-stone-700'
                    }`}
                    data-testid="notification-toggle"
                  >
                    <span className="flex items-center gap-2">
                      {isSubscribed ? (
                        <>
                          <Check size={18} weight="bold" className="text-green-500" />
                          Notifications On
                        </>
                      ) : (
                        <>
                          <X size={18} weight="bold" className="text-stone-500" />
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
                      className="w-full p-3 bg-stone-800 border border-stone-700 rounded-lg text-stone-400 hover:bg-stone-700 hover:text-stone-200 transition-all text-sm"
                      data-testid="notification-test"
                    >
                      Send Test Notification
                    </button>
                  )}
                </>
              )}
            </div>

            <div className="px-4 py-3 bg-stone-800/50 border-t border-stone-700">
              <p className="text-stone-500 text-xs">
                You'll receive notifications even when the app is closed
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
