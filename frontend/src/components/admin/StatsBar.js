import { Users, SealCheck, Article, ChatCircle, Handshake, Envelope } from '@phosphor-icons/react';
import StatCard from './StatCard';

export default function StatsBar({ stats }) {
  return (
    <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-4">
      <StatCard
        icon={Users}
        label="Users"
        value={stats?.total_users || 0}
        subValue={`+${stats?.new_users_week || 0} this week`}
        color="var(--brand-primary)"
      />
      <StatCard icon={SealCheck} label="Verified" value={stats?.verified_users || 0} color="var(--brand-accent)" />
      <StatCard icon={Article} label="Posts" value={stats?.total_posts || 0} color="#0369A1" />
      <StatCard icon={ChatCircle} label="Messages" value={stats?.total_messages || 0} color="#7C3AED" />
      <StatCard icon={Handshake} label="Connections" value={stats?.total_connections || 0} color="#DC2626" />
      <StatCard
        icon={Envelope}
        label="Invites"
        value={stats?.total_invites || 0}
        subValue={`${stats?.used_invites || 0} used`}
        color="#059669"
      />
    </div>
  );
}
