import { useState } from 'react';
import { DeviceMobile, X, Share, Plus } from '@phosphor-icons/react';
import { usePWA } from '../contexts/PWAContext';

export default function InstallAppButton({ compact = false }) {
  const { isInstallable, isInstalled, isIOS, promptInstall, canShowInstallButton } = usePWA();
  const [showIOSModal, setShowIOSModal] = useState(false);

  const handleInstallClick = async () => {
    if (isIOS) {
      setShowIOSModal(true);
    } else {
      const result = await promptInstall();
      console.log('Install prompt result:', result);
    }
  };

  if (!canShowInstallButton) {
    return null;
  }

  return (
    <>
      <button
        onClick={handleInstallClick}
        className={`nav-link w-full text-[var(--brand-primary)] hover:bg-[var(--brand-primary)]/10 ${compact ? 'py-2' : ''}`}
        data-testid="install-app-button"
      >
        <DeviceMobile size={20} weight="duotone" />
        <span>Install App</span>
      </button>

      {/* iOS Install Instructions Modal */}
      {showIOSModal && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4"
          onClick={() => setShowIOSModal(false)}
        >
          <div 
            className="bg-[var(--bg-surface)] rounded-t-2xl sm:rounded-2xl max-w-md w-full p-6 animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-[var(--text-primary)]">Install Rebel Trade Network</h3>
              <button
                onClick={() => setShowIOSModal(false)}
                className="p-2 rounded-full hover:bg-[var(--bg-surface-hover)] transition-colors"
              >
                <X size={20} className="text-[var(--text-muted)]" />
              </button>
            </div>

            <p className="text-[var(--text-secondary)] mb-6">
              Install this app on your iPhone for quick access and a native app experience.
            </p>

            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-[var(--brand-primary)]/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-[var(--brand-primary)] font-bold">1</span>
                </div>
                <div>
                  <p className="text-[var(--text-primary)] font-medium">Tap the Share button</p>
                  <p className="text-sm text-[var(--text-muted)] flex items-center gap-1">
                    Look for <Share size={16} weight="bold" className="text-[var(--brand-primary)]" /> in your browser toolbar
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-[var(--brand-primary)]/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-[var(--brand-primary)] font-bold">2</span>
                </div>
                <div>
                  <p className="text-[var(--text-primary)] font-medium">Scroll down and tap</p>
                  <p className="text-sm text-[var(--text-muted)] flex items-center gap-1">
                    <Plus size={16} weight="bold" className="text-[var(--brand-primary)]" /> "Add to Home Screen"
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-[var(--brand-primary)]/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-[var(--brand-primary)] font-bold">3</span>
                </div>
                <div>
                  <p className="text-[var(--text-primary)] font-medium">Tap "Add" to confirm</p>
                  <p className="text-sm text-[var(--text-muted)]">
                    The app will appear on your home screen
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setShowIOSModal(false)}
              className="w-full mt-6 btn-primary"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes slide-up {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
    </>
  );
}
