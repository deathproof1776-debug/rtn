import { useState } from 'react';
import { DeviceMobile, X, Share, Plus, Check, Desktop, AndroidLogo, AppleLogo } from '@phosphor-icons/react';
import { usePWA } from '../contexts/PWAContext';

export default function InstallAppButton({ compact = false }) {
  const { isInstallable, isInstalled, isIOS, promptInstall } = usePWA();
  const [showModal, setShowModal] = useState(false);

  // Detect platform for instructions
  const isAndroid = /Android/.test(navigator.userAgent);
  const isDesktop = !isIOS && !isAndroid;

  const handleInstallClick = async () => {
    if (isInstalled) {
      // Already installed - show confirmation
      return;
    }
    
    if (isInstallable) {
      // Chrome/Edge - can prompt directly
      const result = await promptInstall();
      console.log('Install prompt result:', result);
    } else {
      // Show manual instructions modal
      setShowModal(true);
    }
  };

  // Always show the button (unless already installed as standalone)
  if (isInstalled) {
    return (
      <div className={`nav-link w-full text-green-500 cursor-default ${compact ? 'py-2' : ''}`}>
        <Check size={20} weight="bold" />
        <span>App Installed</span>
      </div>
    );
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

      {/* Install Instructions Modal */}
      {showModal && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4"
          onClick={() => setShowModal(false)}
        >
          <div 
            className="bg-[var(--bg-surface)] rounded-t-2xl sm:rounded-2xl max-w-md w-full p-6 animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-[var(--text-primary)]">Install Rebel Trade Network</h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 rounded-full hover:bg-[var(--bg-surface-hover)] transition-colors"
              >
                <X size={20} className="text-[var(--text-muted)]" />
              </button>
            </div>

            {/* Platform indicator */}
            <div className="flex items-center gap-2 mb-4 text-sm text-[var(--text-muted)]">
              {isIOS && <><AppleLogo size={18} /> iOS / Safari</>}
              {isAndroid && <><AndroidLogo size={18} /> Android / Chrome</>}
              {isDesktop && <><Desktop size={18} /> Desktop Browser</>}
            </div>

            <p className="text-[var(--text-secondary)] mb-6">
              {isIOS 
                ? "Install this app on your iPhone for quick access and a native app experience."
                : isAndroid
                ? "Install this app on your Android device for quick access."
                : "Install this app on your computer for quick access from your desktop."
              }
            </p>

            <div className="space-y-4">
              {isIOS ? (
                <>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-[var(--brand-primary)]/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-[var(--brand-primary)] font-bold">1</span>
                    </div>
                    <div>
                      <p className="text-[var(--text-primary)] font-medium">Tap the Share button</p>
                      <p className="text-sm text-[var(--text-muted)] flex items-center gap-1">
                        Look for <Share size={16} weight="bold" className="text-[var(--brand-primary)]" /> in Safari's toolbar
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
                </>
              ) : (
                <>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-[var(--brand-primary)]/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-[var(--brand-primary)] font-bold">1</span>
                    </div>
                    <div>
                      <p className="text-[var(--text-primary)] font-medium">Look for the install icon</p>
                      <p className="text-sm text-[var(--text-muted)]">
                        {isAndroid 
                          ? "In Chrome, tap the menu (⋮) and look for 'Install app' or 'Add to Home screen'"
                          : "In your browser's address bar, look for the install icon (⊕) or check the menu"
                        }
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-[var(--brand-primary)]/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-[var(--brand-primary)] font-bold">2</span>
                    </div>
                    <div>
                      <p className="text-[var(--text-primary)] font-medium">Click "Install"</p>
                      <p className="text-sm text-[var(--text-muted)]">
                        Confirm the installation when prompted
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-[var(--brand-primary)]/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-[var(--brand-primary)] font-bold">3</span>
                    </div>
                    <div>
                      <p className="text-[var(--text-primary)] font-medium">Launch from {isAndroid ? 'home screen' : 'desktop'}</p>
                      <p className="text-sm text-[var(--text-muted)]">
                        The app will open in its own window
                      </p>
                    </div>
                  </div>
                </>
              )}
            </div>

            <button
              onClick={() => setShowModal(false)}
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
