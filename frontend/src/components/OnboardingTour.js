import { useState } from 'react';
import axios from 'axios';
import {
  Handshake, House, ArrowsLeftRight, Newspaper, ChatCircle,
  ArrowRight, ArrowLeft, X, Shield
} from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STEPS = [
  {
    icon: Shield,
    title: 'Welcome to Rebel Trade Network',
    body: 'A private, invite-only network where homesteaders and self-reliant folks barter goods, skills, and services — no corporate middlemen, no fees.'
  },
  {
    icon: House,
    title: 'Barter Feed & Smart Matches',
    body: 'Post what you\'re offering and what you\'re looking for. The feed surfaces nearby traders and complementary matches so you find the right exchange faster.'
  },
  {
    icon: ArrowsLeftRight,
    title: 'Trade Network & Deals',
    body: 'Connect with other traders, then propose formal trade deals with counter-offers. Complete 5 confirmed trades to earn your Trusted Trader badge.'
  },
  {
    icon: Newspaper,
    title: 'Community, Messages & Safety',
    body: 'Join topic discussions on the Community Board, chat privately with end-to-end encrypted messages, and keep the network safe with report & block tools.'
  }
];

export default function OnboardingTour({ onComplete }) {
  const [step, setStep] = useState(0);
  const [finishing, setFinishing] = useState(false);
  const isLast = step === STEPS.length - 1;
  const Current = STEPS[step];
  const Icon = Current.icon;

  const finish = async () => {
    setFinishing(true);
    try {
      await axios.post(`${API_URL}/api/onboarding/complete`, {}, { withCredentials: true });
    } catch (_) { /* non-blocking */ }
    onComplete?.();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" data-testid="onboarding-tour">
      <div className="relative w-full max-w-md bg-[var(--bg-surface)] border-2 border-[var(--brand-primary)] shadow-2xl">
        <button
          onClick={finish}
          className="absolute top-3 right-3 p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
          aria-label="Skip tour"
          data-testid="onboarding-skip"
        >
          <X size={18} />
        </button>

        <div className="px-6 pt-8 pb-6 text-center">
          <div className="w-16 h-16 mx-auto mb-5 flex items-center justify-center bg-[var(--brand-primary)]/15 border border-[var(--brand-primary)]/40 rounded-full">
            <Icon size={32} weight="duotone" className="text-[var(--brand-primary)]" />
          </div>
          <h2
            className="text-xl font-bold text-[var(--text-primary)] mb-3"
            style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}
            data-testid="onboarding-title"
          >
            {Current.title}
          </h2>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{Current.body}</p>
        </div>

        {/* Progress dots */}
        <div className="flex items-center justify-center gap-2 pb-5">
          {STEPS.map((_, i) => (
            <span
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === step ? 'w-6 bg-[var(--brand-primary)]' : 'w-1.5 bg-[var(--border-color)]'
              }`}
            />
          ))}
        </div>

        <div className="flex items-center justify-between gap-3 px-6 py-4 border-t border-[var(--border-color)]">
          <button
            onClick={finish}
            className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            data-testid="onboarding-skip-text"
          >
            Skip
          </button>
          <div className="flex items-center gap-2">
            {step > 0 && (
              <button
                onClick={() => setStep(step - 1)}
                className="px-3 py-2 text-xs flex items-center gap-1 border border-[var(--border-color)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)]"
                data-testid="onboarding-back"
              >
                <ArrowLeft size={14} /> Back
              </button>
            )}
            {isLast ? (
              <button
                onClick={finish}
                disabled={finishing}
                className="btn-primary px-4 py-2 text-xs flex items-center gap-1 disabled:opacity-60"
                data-testid="onboarding-finish"
              >
                <Handshake size={14} /> Start Trading
              </button>
            ) : (
              <button
                onClick={() => setStep(step + 1)}
                className="btn-primary px-4 py-2 text-xs flex items-center gap-1"
                data-testid="onboarding-next"
              >
                Next <ArrowRight size={14} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
