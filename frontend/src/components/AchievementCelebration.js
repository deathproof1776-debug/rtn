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
    earned: 'An admin reviewed and verified your account.',
    description: 'Verification is a trust signal shown across the network. It tells other members you\'re a real, vetted trader — which means more responses, more matches, and smoother deals.',
    perks: [
      'An orange Verified badge appears on your posts, profile, and comments',
      'You can now send invite links to bring trusted people into the network',
      'Verified traders rank higher in the Barter Feed and match suggestions',
      'Other members are far more likely to accept your trade & connection requests'
    ],
    tip: 'Tip: Complete your profile — location, skills, and what you offer/need — to unlock the best matches.'
  },
  trusted_trader: {
    icon: Handshake,
    color: '#4D7C0F',
    badge: 'Trusted Trader',
    title: 'Trusted Trader Unlocked! 🤝',
    earned: 'You completed 5 trades that both parties confirmed.',
    description: 'The green Trusted Trader badge is the highest reputation signal on Rebel Trade Network. It\'s earned, not given — it tells everyone you follow through and trade fairly.',
    perks: [
      'An exclusive green Trusted Trader badge on your profile and every post',
      'Top priority placement in the feed and recommended-trader lists',
      'Higher acceptance rates on connections, messages, and trade offers',
      'A visible track record that builds instant credibility with new partners'
    ],
    tip: 'Keep it up: the badge reflects ongoing good standing — honor your agreements and confirm trades promptly.'
  },
  moderator: {
    icon: ShieldStar,
    color: '#0369A1',
    badge: 'Moderator',
    title: "You're now a Moderator 🛡",
    earned: 'An admin promoted you — a role reserved for verified, trusted members.',
    description: 'You\'ve been entrusted to help keep Rebel Trade Network safe and welcoming. Look for the new "Moderation" tab in your sidebar to access the report queue.',
    perks: [
      'Review, resolve, and dismiss community reports from the Moderation queue',
      'Escalate serious or unclear reports to an admin for a final decision',
      'Remove flagged posts and comments directly from the feed',
      'Help set the tone and standard for the whole community'
    ],
    tip: 'Please note: blocking/banning users, verifying members, and system announcements remain admin-only. Escalated reports can only be closed by an admin.'
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
        className="relative w-full max-w-sm max-h-[92vh] overflow-y-auto bg-[var(--bg-surface)] border-2 shadow-2xl"
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
          {cfg.earned && (
            <p className="text-[11px] text-[var(--text-muted)] italic mb-2">{cfg.earned}</p>
          )}
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{cfg.description}</p>
        </div>

        <div className="px-6 pb-4">
          <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-2">
            What this unlocks
          </p>
          <div className="bg-[var(--bg-surface-hover)] border border-[var(--border-color)] p-3 space-y-2">
            {cfg.perks.map((perk) => (
              <div key={perk} className="flex items-start gap-2 text-xs text-[var(--text-secondary)]">
                <span className="mt-0.5" style={{ color: cfg.color }}>✦</span>
                <span>{perk}</span>
              </div>
            ))}
          </div>
          {cfg.tip && (
            <p className="mt-3 text-[11px] text-[var(--text-muted)] leading-relaxed">{cfg.tip}</p>
          )}
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
