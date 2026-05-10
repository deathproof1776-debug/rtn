import { useState } from 'react';

export default function AnnouncementModal({ message, onClose, onSave, onDelete }) {
  const [formData, setFormData] = useState({
    message: message?.message || '',
    type: message?.type || 'info',
    priority: message?.priority || 0,
    is_active: message?.is_active ?? true
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.message.trim()) return;
    setSaving(true);
    await onSave(formData);
    setSaving(false);
  };

  const typeColors = {
    info: 'border-blue-500 bg-blue-500/10',
    warning: 'border-yellow-500 bg-yellow-500/10',
    success: 'border-green-500 bg-green-500/10',
    urgent: 'border-red-500 bg-red-500/10'
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60">
      <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-4 max-w-md mx-4 w-full">
        <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">
          {message ? 'Edit Announcement' : 'New Announcement'}
        </h3>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Message</label>
            <textarea
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="input-field w-full h-20 resize-none text-sm"
              placeholder="Enter announcement..."
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="input-field w-full text-sm"
              >
                <option value="info">Info</option>
                <option value="success">Success</option>
                <option value="warning">Warning</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Priority</label>
              <input
                type="number"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                className="input-field w-full text-sm"
                min="0" max="100"
              />
            </div>
          </div>

          <div className={`p-2 border-l-4 text-xs ${typeColors[formData.type]}`}>
            <p className="text-[var(--text-primary)]">{formData.message || 'Preview...'}</p>
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4"
              />
              <label htmlFor="is_active" className="text-xs text-[var(--text-secondary)]">Active</label>
            </div>

            <div className="flex gap-2">
              {message && onDelete && (
                <button type="button" onClick={onDelete} className="text-xs text-red-400 hover:text-red-300 px-2">
                  Delete
                </button>
              )}
              <button type="button" onClick={onClose} className="btn-secondary px-3 py-1.5 text-xs">Cancel</button>
              <button type="submit" disabled={saving || !formData.message.trim()} className="btn-primary px-3 py-1.5 text-xs">
                {saving ? '...' : message ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
