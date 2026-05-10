export default function StatCard({ icon: Icon, label, value, subValue, color }) {
  return (
    <div
      className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-3"
      data-testid={`stat-${label.toLowerCase().replace(/\s+/g, '-')}`}
    >
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          <Icon size={16} style={{ color }} weight="duotone" />
        </div>
        <div>
          <p className="text-xl font-bold text-[var(--text-primary)]">{value}</p>
          <p className="text-[10px] text-[var(--text-muted)]">{label}</p>
        </div>
      </div>
      {subValue && (
        <p className="text-[9px] text-[var(--text-muted)] mt-1 pt-1 border-t border-[var(--border-color)]">{subValue}</p>
      )}
    </div>
  );
}
