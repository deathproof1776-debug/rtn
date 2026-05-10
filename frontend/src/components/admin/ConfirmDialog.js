import { Warning } from '@phosphor-icons/react';

export default function ConfirmDialog({ action, onCancel, onConfirm }) {
  if (!action) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60">
      <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 max-w-sm mx-4 w-full">
        <div className="flex items-center gap-2 mb-3">
          <Warning size={18} className="text-red-400" />
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">Confirm Action</h3>
        </div>
        <p className="text-xs text-[var(--text-secondary)] mb-4">{action.label}</p>
        <div className="flex gap-2 justify-end">
          <button onClick={onCancel} className="btn-secondary px-3 py-1.5 text-xs">Cancel</button>
          <button
            onClick={onConfirm}
            className="px-3 py-1.5 text-xs font-medium bg-red-600 hover:bg-red-700 text-white"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
