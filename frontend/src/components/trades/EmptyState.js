/**
 * EmptyState - Reusable empty state component for trade panels
 */
export default function EmptyState({ icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center" data-testid="empty-state">
      {icon}
      <p className="text-[var(--text-primary)] font-medium mt-3">{title}</p>
      <p className="text-sm text-[var(--text-muted)] mt-1">{subtitle}</p>
    </div>
  );
}
