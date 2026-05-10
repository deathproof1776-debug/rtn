import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Images, Plus, Camera, CaretLeft } from '@phosphor-icons/react';
import { toast } from 'sonner';
import GalleryGrid from './gallery/GalleryGrid';
import GalleryItemModal from './gallery/GalleryItemModal';
import UploadModal from './gallery/UploadModal';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Gallery({ userId, isOwnProfile = false, onBack }) {
  const { user: currentUser } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [userName, setUserName] = useState('');

  const fetchGallery = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/gallery/user/${userId}`, {
        withCredentials: true
      });
      setItems(response.data.items);
      setUserName(response.data.user_name);
    } catch (error) {
      console.error('Error fetching gallery:', error);
      toast.error('Failed to load gallery');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchGallery();
  }, [fetchGallery]);

  const handleLike = async (itemId) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/gallery/${itemId}/like`,
        {},
        { withCredentials: true }
      );
      setItems(items.map(item =>
        item.id === itemId
          ? { ...item, is_liked: response.data.action === 'liked', like_count: response.data.like_count }
          : item
      ));
    } catch (error) {
      console.error('Error liking item:', error);
    }
  };

  const handleItemClick = async (item) => {
    try {
      const response = await axios.get(`${API_URL}/api/gallery/item/${item.id}`, {
        withCredentials: true
      });
      setSelectedItem(response.data);
    } catch (error) {
      console.error('Error fetching item details:', error);
      setSelectedItem(item);
    }
  };

  const handleUploadComplete = (newItem) => {
    setItems([{
      id: newItem.id,
      url: newItem.url,
      is_video: newItem.is_video,
      caption: newItem.caption,
      like_count: 0,
      comment_count: 0,
      is_liked: false,
      created_at: new Date().toISOString()
    }, ...items]);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-[var(--brand-primary)] border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col" data-testid="gallery-panel">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        {onBack && (
          <button
            onClick={onBack}
            className="p-2 hover:bg-[var(--bg-surface-hover)] rounded-lg"
            data-testid="gallery-back-btn"
          >
            <CaretLeft size={20} className="text-[var(--text-secondary)]" />
          </button>
        )}
        <Images size={24} weight="duotone" className="text-[var(--brand-primary)]" />
        <h2 className="text-xl font-bold text-[var(--text-primary)]">
          {isOwnProfile ? 'My Gallery' : `${userName}'s Gallery`}
        </h2>
        {isOwnProfile && (
          <button
            onClick={() => setShowUpload(true)}
            className="ml-auto p-2 bg-[var(--brand-primary)] text-white rounded-lg hover:opacity-90"
            data-testid="gallery-upload-btn"
          >
            <Plus size={20} />
          </button>
        )}
      </div>

      {/* Gallery Grid */}
      {items.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
          <Images size={64} className="text-[var(--text-muted)] mb-4" />
          <p className="text-[var(--text-secondary)] mb-2">
            {isOwnProfile ? 'Your gallery is empty' : 'No photos or videos yet'}
          </p>
          {isOwnProfile && (
            <button
              onClick={() => setShowUpload(true)}
              className="mt-4 px-4 py-2 bg-[var(--brand-primary)] text-white rounded-lg flex items-center gap-2"
            >
              <Camera size={18} />
              Upload your first photo
            </button>
          )}
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <GalleryGrid
            items={items}
            onItemClick={handleItemClick}
            onLike={handleLike}
          />
        </div>
      )}

      {/* Modals */}
      {selectedItem && (
        <GalleryItemModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
          onLike={(itemId, data) => {
            setItems(items.map(item =>
              item.id === itemId
                ? { ...item, is_liked: data.action === 'liked', like_count: data.like_count }
                : item
            ));
          }}
          onComment={(itemId) => {
            setItems(items.map(item =>
              item.id === itemId
                ? { ...item, comment_count: item.comment_count + 1 }
                : item
            ));
          }}
          currentUserId={currentUser?.id}
        />
      )}

      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUpload={handleUploadComplete}
        />
      )}
    </div>
  );
}
