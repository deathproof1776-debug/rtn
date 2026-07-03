import { useState } from 'react';
import axios from 'axios';
import { SealCheck, Handshake, ShieldStar, Sparkle } from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ACHIEVEMENTS = {
  verified: {
    icon: SealCheck,
    color: 'var(--brand-primary)',
    badge: 'Verified Trader',
    title: "You're Verified! ✓",
    description: 'An admin has verified your account — a trust signal other traders can see on your posts and profile.',
    perks: [
      'A verified badge appears across your posts & profile',
      'You can now invite new members to the network',
      'Higher visibility in the Barter Feed'
    ]
  },
  trusted_trader: {
    icon: Handshake,
    color: '#4D7C0F',
    badge: 'Trusted Trader',
    title: 'Trusted Trader Unlocked! 🤝',
    description: "You've completed 5 confirmed trades. This green badge tells the community you're a reliable partner.",
    perks: [
      'Exclusive green Trusted Trader badge',
      'Stronger reputation on every trade',
      'Boosted trust with new trading partners'
    ]
  },
  moderator: {
    icon: ShieldStar,
    color: '#0369A1',
    badge: 'Moderator',
    title: "You're now a Moderator 🛡",
    description: 'You\'ve been trusted to help keep Rebel Trade Network safe. Find the Moderation queue in your sidebar.',
    perks: [
      'Review, resolve & dismiss community reports',
      'Escalate serious reports to an admin',
      'Remove flagged posts and comments'
    ]
  }
};

export default function AchievementCelebration({ achievementKey, onAck }) {
  const [dismissing, setDismissing] = useState(false);
  const cfg = ACHIEVEMENTS[achievementKey];
  if (!cfg) return null;
  const Icon = cfg.icon;

  const dismiss = async () => {
    setDismissing(true);
    try {
      await axios.post(`${API_URL}/api/achievements/ack`, { key: achievementKey }, { withCredentials: true });
    } catch (_) { /* non-blocking */ }
    onAck?.(achievementKey);
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/75 backdrop-blur-sm p-4" data-testid="achievement-celebration">
      <div
        className="relative w-full max-w-sm bg-[var(--bg-surface)] border-2 shadow-2xl overflow-hidden"
        style={{ borderColor: cfg.color }}
      >
        <div className="absolute -top-10 -right-10 opacity-10">
          <Sparkle size={140} weight="fill" style={{ color: cfg.color }} />
        </div>

        <div className="px-6 pt-8 pb-4 text-center relative">
          <div
            className="w-20 h-20 mx-auto mb-4 flex items-center justify-center rounded-full"
            style={{ backgroundColor: `${cfg.color}22`, border: `2px solid ${cfg.color}` }}
          >
            <Icon size={40} weight="fill" style={{ color: cfg.color }} />
          </div>
          <p className="text-[10px] font-bold uppercase tracking-widest mb-1" style={{ color: cfg.color }}>
            Achievement Unlocked
          </p>
          <h2
            className="text-xl font-bold text-[var(--text-primary)] mb-2"
            style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}
            data-testid="achievement-title"
          >
            {cfg.title}
          </h2>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{cfg.description}</p>
        </div>

        <div className="px-6 pb-5">
          <div className="bg-[var(--bg-surface-hover)] border border-[var(--border-color)] p-3 space-y-2">
            {cfg.perks.map((perk, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-[var(--text-secondary)]">
                <span className="mt-0.5" style={{ color: cfg.color }}>✦</span>
                <span>{perk}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="px-6 pb-6">
          <button
            onClick={dismiss}
            disabled={dismissing}
            className="btn-primary w-full py-2.5 text-sm disabled:opacity-60"
            data-testid="achievement-dismiss"
          >
            Awesome!
          </button>
        </div>
      </div>
    </div>
  );
}
