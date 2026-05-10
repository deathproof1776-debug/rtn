import { Heart, ChatCircle, Play } from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function GalleryGrid({ items, onItemClick, onLike }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
      {items.map((item) => (
        <div
          key={item.id}
          className="relative aspect-square bg-[var(--bg-surface)] rounded-lg overflow-hidden cursor-pointer group"
          onClick={() => onItemClick(item)}
          data-testid={`gallery-item-${item.id}`}
        >
          {item.is_video ? (
            <div className="w-full h-full flex items-center justify-center bg-black">
              <video
                src={`${API_URL}${item.url}`}
                className="w-full h-full object-cover"
                preload="metadata"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-12 h-12 bg-black/60 rounded-full flex items-center justify-center">
                  <Play size={24} weight="fill" className="text-white ml-1" />
                </div>
              </div>
            </div>
          ) : (
            <img
              src={`${API_URL}${item.url}`}
              alt={item.caption || 'Gallery item'}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          )}

          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onLike(item.id);
              }}
              className="flex items-center gap-1 text-white"
              data-testid={`gallery-like-${item.id}`}
            >
              <Heart
                size={20}
                weight={item.is_liked ? 'fill' : 'regular'}
                className={item.is_liked ? 'text-red-500' : 'text-white'}
              />
              <span>{item.like_count}</span>
            </button>
            <div className="flex items-center gap-1 text-white">
              <ChatCircle size={20} />
              <span>{item.comment_count}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
