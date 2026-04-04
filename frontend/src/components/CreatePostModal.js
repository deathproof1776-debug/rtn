import { useState, useRef } from 'react';
import { X, Image, Tag, ArrowsLeftRight } from '@phosphor-icons/react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import CategorySelector from './CategorySelector';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORIES = [
  { value: 'goods', label: 'Goods' },
  { value: 'services', label: 'Services' },
  { value: 'skills', label: 'Skills' },
];

export default function CreatePostModal({ onClose, onPostCreated, editPost = null }) {
  const { user } = useAuth();
  const [title, setTitle] = useState(editPost?.title || '');
  const [description, setDescription] = useState(editPost?.description || '');
  const [category, setCategory] = useState(editPost?.category || 'goods');
  const [offering, setOffering] = useState(editPost?.offering || []);
  const [lookingFor, setLookingFor] = useState(editPost?.looking_for || []);
  const [images, setImages] = useState(editPost?.images || []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const isEditing = !!editPost;

  const handleImageUpload = async (e) => {
    const files = Array.from(e.target.files);
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await axios.post(`${API_URL}/api/upload`, formData, {
          withCredentials: true,
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setImages([...images, `${API_URL}${response.data.url}`]);
      } catch (err) {
        console.error('Error uploading image:', err);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (offering.length === 0) {
      setError('Add at least one item you are offering');
      return;
    }

    if (lookingFor.length === 0) {
      setError('Add at least one item you are looking for');
      return;
    }

    setLoading(true);

    try {
      if (isEditing) {
        // Update existing post
        await axios.put(`${API_URL}/api/posts/${editPost._id}`, {
          title,
          description,
          category,
          offering,
          looking_for: lookingFor,
          images
        }, { withCredentials: true });

        onPostCreated({
          ...editPost,
          title,
          description,
          category,
          offering,
          looking_for: lookingFor,
          images,
          updated_at: new Date().toISOString()
        });
      } else {
        // Create new post
        const response = await axios.post(`${API_URL}/api/posts`, {
          title,
          description,
          category,
          offering,
          looking_for: lookingFor,
          images
        }, { withCredentials: true });

        onPostCreated({
          _id: response.data.id,
          user_id: user?.id,
          user_name: user?.name || 'Anonymous',
          user_avatar: user?.avatar || '',
          title,
          description,
          category,
          offering,
          looking_for: lookingFor,
          images,
          created_at: new Date().toISOString(),
          likes: [],
          comments: []
        });
      }
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} post`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" data-testid="create-post-modal">
      <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-hover)] w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <div className="flex items-center justify-between p-4 border-b border-[var(--bg-surface-hover)]">
          <h2 className="text-xl font-bold text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            {isEditing ? 'Edit Barter Post' : 'Create Barter Post'}
          </h2>
          <button onClick={onClose} className="btn-ghost p-2" data-testid="close-modal">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="bg-[var(--brand-danger)]/20 border border-[var(--brand-danger)] text-[var(--text-primary)] px-4 py-3">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-2">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input-field w-full"
              placeholder="What are you bartering?"
              data-testid="post-title-input"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-2">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input-field w-full h-24 resize-none"
              placeholder="Describe what you have and what you're looking for..."
              data-testid="post-description-input"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-2">Category</label>
            <div className="flex gap-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => setCategory(cat.value)}
                  className={`px-4 py-2 border ${
                    category === cat.value 
                      ? 'bg-[var(--brand-primary)] border-[var(--brand-primary)] text-[var(--text-primary)]' 
                      : 'bg-[var(--bg-main)] border-[var(--bg-surface-active)] text-[var(--text-secondary)]'
                  }`}
                  data-testid={`category-${cat.value}`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Offering Section - Using CategorySelector */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Tag size={16} className="text-[var(--brand-accent)]" />
              <label className="text-sm text-[var(--text-secondary)]">What You're Offering</label>
            </div>
            <CategorySelector
              type={category === 'skills' ? 'skills' : category === 'services' ? 'services' : 'goods'}
              mode="offering"
              selectedItems={offering}
              onItemsChange={setOffering}
              placeholder="Search or add items you're offering..."
              maxDisplay={10}
            />
          </div>

          {/* Looking For Section - Using CategorySelector */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <ArrowsLeftRight size={16} className="text-[var(--brand-primary)]" />
              <label className="text-sm text-[var(--text-secondary)]">What You're Looking For</label>
            </div>
            <CategorySelector
              type={category === 'skills' ? 'skills' : category === 'services' ? 'services' : 'goods'}
              mode="wanted"
              selectedItems={lookingFor}
              onItemsChange={setLookingFor}
              placeholder="Search or add items you're looking for..."
              maxDisplay={10}
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-2">
              <Image size={16} className="inline mr-1" />
              Images (optional)
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleImageUpload}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="btn-secondary w-full flex items-center justify-center gap-2"
              data-testid="upload-images-button"
            >
              <Image size={20} />
              Upload Images
            </button>
            {images.length > 0 && (
              <div className="grid grid-cols-4 gap-2 mt-2">
                {images.map((img, i) => (
                  <div key={`upload-img-${img.slice(-20)}-${i}`} className="relative">
                    <img src={img} alt="" className="w-full h-20 object-cover border border-[var(--bg-surface-hover)]" />
                    <button
                      type="button"
                      onClick={() => setImages(images.filter((_, idx) => idx !== i))}
                      className="absolute -top-2 -right-2 w-5 h-5 bg-[var(--brand-danger)] flex items-center justify-center"
                    >
                      <X size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary flex-1" data-testid="cancel-post">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary flex-1" data-testid="submit-post">
              {loading ? (isEditing ? 'Saving...' : 'Creating...') : (isEditing ? 'Save Changes' : 'Create Post')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
