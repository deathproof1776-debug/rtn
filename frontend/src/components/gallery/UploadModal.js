import { useState, useRef } from 'react';
import axios from 'axios';
import { X, Camera } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
const VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/webm', 'video/mpeg'];

export default function UploadModal({ onClose, onUpload }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [caption, setCaption] = useState('');
  const [uploading, setUploading] = useState(false);
  const [isVideo, setIsVideo] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    const allowedTypes = [...IMAGE_TYPES, ...VIDEO_TYPES];
    if (!allowedTypes.includes(selectedFile.type)) {
      toast.error('Invalid file type. Allowed: JPEG, PNG, GIF, WebP, MP4, MOV, WebM');
      return;
    }

    const maxSize = VIDEO_TYPES.includes(selectedFile.type) ? 100 * 1024 * 1024 : 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      toast.error(`File too large. Max size: ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    setFile(selectedFile);
    setIsVideo(VIDEO_TYPES.includes(selectedFile.type));
    setPreview(URL.createObjectURL(selectedFile));
  };

  const handleUpload = async () => {
    if (!file || uploading) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('caption', caption);

    try {
      const response = await axios.post(`${API_URL}/api/gallery/upload`, formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Uploaded successfully');
      onUpload(response.data);
      onClose();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80"
      onClick={onClose}
    >
      <div
        className="bg-[var(--bg-surface)] rounded-lg overflow-hidden max-w-lg w-full"
        onClick={(e) => e.stopPropagation()}
        data-testid="gallery-upload-modal"
      >
        <div className="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
          <h3 className="font-semibold text-[var(--text-primary)]">Upload to Gallery</h3>
          <button onClick={onClose} className="p-1 hover:bg-[var(--bg-surface-hover)] rounded">
            <X size={20} className="text-[var(--text-secondary)]" />
          </button>
        </div>

        <div className="p-4">
          {!preview ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-[var(--border-color)] rounded-lg p-8 text-center cursor-pointer hover:border-[var(--brand-primary)] transition-colors"
            >
              <Camera size={48} className="mx-auto text-[var(--text-muted)] mb-2" />
              <p className="text-[var(--text-secondary)]">Click to select a photo or video</p>
              <p className="text-xs text-[var(--text-muted)] mt-1">
                Images: JPEG, PNG, GIF, WebP (max 10MB)<br />
                Videos: MP4, MOV, WebM (max 100MB)
              </p>
            </div>
          ) : (
            <div className="relative">
              {isVideo ? (
                <video
                  src={preview}
                  className="w-full rounded-lg max-h-64 object-contain bg-black"
                  controls
                />
              ) : (
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full rounded-lg max-h-64 object-contain"
                />
              )}
              <button
                onClick={() => {
                  setFile(null);
                  setPreview(null);
                }}
                className="absolute top-2 right-2 p-1 bg-black/50 rounded-full hover:bg-black/70"
              >
                <X size={16} className="text-white" />
              </button>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp,video/mp4,video/quicktime,video/webm"
            onChange={handleFileSelect}
            className="hidden"
            data-testid="gallery-file-input"
          />

          {preview && (
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Write a caption..."
              className="w-full mt-4 p-3 bg-[var(--bg-main)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-muted)] resize-none"
              rows={2}
              data-testid="gallery-caption-input"
            />
          )}
        </div>

        <div className="p-4 border-t border-[var(--border-color)] flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-4 py-2 bg-[var(--brand-primary)] text-white rounded-lg disabled:opacity-50 flex items-center gap-2"
            data-testid="gallery-upload-submit"
          >
            {uploading ? 'Uploading...' : 'Share'}
          </button>
        </div>
      </div>
    </div>
  );
}
