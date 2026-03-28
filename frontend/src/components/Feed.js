import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  Heart, 
  ChatCircle, 
  DotsThree,
  Plus,
  MapPin,
  Tag,
  ArrowsLeftRight
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Feed({ posts, loading, onCreatePost }) {
  const { user } = useAuth();

  const handleLike = async (postId) => {
    try {
      await axios.post(`${API_URL}/api/posts/${postId}/like`, {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="post-card animate-pulse">
            <div className="h-4 bg-[#292524] w-1/3 mb-4"></div>
            <div className="h-3 bg-[#292524] w-full mb-2"></div>
            <div className="h-3 bg-[#292524] w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div data-testid="feed">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Barter Feed
          </h2>
          <p className="text-sm text-[#78716C] mt-1">Connect. Trade. Thrive.</p>
        </div>
        <button
          onClick={onCreatePost}
          className="btn-primary flex items-center gap-2 md:hidden"
          data-testid="create-post-mobile"
        >
          <Plus size={18} weight="bold" />
          Post
        </button>
      </div>

      {posts.length === 0 ? (
        <div className="post-card text-center py-12">
          <ArrowsLeftRight size={48} className="mx-auto text-[#44403C] mb-4" />
          <h3 className="text-lg font-semibold text-[#E7E5E4] mb-2">No barter posts yet</h3>
          <p className="text-sm text-[#78716C] mb-4">Be the first to share what you can offer or need</p>
          <button onClick={onCreatePost} className="btn-primary" data-testid="create-first-post">
            Create Your First Post
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard key={post._id} post={post} onLike={handleLike} currentUserId={user?.id} />
          ))}
        </div>
      )}
    </div>
  );
}

function PostCard({ post, onLike, currentUserId }) {
  const [liked, setLiked] = useState(post.likes?.includes(currentUserId));
  const [likeCount, setLikeCount] = useState(post.likes?.length || 0);

  const handleLikeClick = async () => {
    await onLike(post._id);
    setLiked(!liked);
    setLikeCount(liked ? likeCount - 1 : likeCount + 1);
  };

  const timeAgo = post.created_at 
    ? formatDistanceToNow(new Date(post.created_at), { addSuffix: true })
    : 'recently';

  return (
    <article className="post-card animate-slide-up" data-testid={`post-${post._id}`}>
      <header className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold text-lg">
            {post.user_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div>
            <h4 className="font-medium text-[#E7E5E4]">{post.user_name || 'Anonymous'}</h4>
            <p className="text-xs text-[#78716C]">{timeAgo}</p>
          </div>
        </div>
        <button className="btn-ghost p-2">
          <DotsThree size={20} weight="bold" />
        </button>
      </header>

      <h3 className="text-lg font-semibold text-[#E7E5E4] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
        {post.title}
      </h3>
      
      <p className="text-[#A8A29E] mb-4 leading-relaxed">{post.description}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        <span className="badge text-xs">{post.category?.toUpperCase()}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="bg-[#0C0A09] p-3 border border-[#292524]">
          <div className="flex items-center gap-2 mb-2">
            <Tag size={16} className="text-[#4D7C0F]" />
            <span className="text-xs uppercase tracking-wider text-[#4D7C0F] font-semibold">Offering</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {post.offering?.map((item, i) => (
              <span key={i} className="badge badge-offering text-xs">{item}</span>
            ))}
          </div>
        </div>
        <div className="bg-[#0C0A09] p-3 border border-[#292524]">
          <div className="flex items-center gap-2 mb-2">
            <ArrowsLeftRight size={16} className="text-[#B45309]" />
            <span className="text-xs uppercase tracking-wider text-[#B45309] font-semibold">Looking For</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {post.looking_for?.map((item, i) => (
              <span key={i} className="badge badge-looking text-xs">{item}</span>
            ))}
          </div>
        </div>
      </div>

      {post.images?.length > 0 && (
        <div className="mb-4 grid grid-cols-2 gap-2">
          {post.images.slice(0, 4).map((img, i) => (
            <img 
              key={i} 
              src={img} 
              alt={`Post image ${i + 1}`}
              className="w-full h-32 object-cover border border-[#292524]"
            />
          ))}
        </div>
      )}

      <footer className="flex items-center gap-4 pt-4 border-t border-[#292524]">
        <button 
          onClick={handleLikeClick}
          className={`btn-ghost flex items-center gap-2 ${liked ? 'text-[#B45309]' : ''}`}
          data-testid={`like-post-${post._id}`}
        >
          <Heart size={20} weight={liked ? 'fill' : 'regular'} />
          <span className="text-sm">{likeCount}</span>
        </button>
        <button className="btn-ghost flex items-center gap-2" data-testid={`comment-post-${post._id}`}>
          <ChatCircle size={20} />
          <span className="text-sm">{post.comments?.length || 0}</span>
        </button>
      </footer>
    </article>
  );
}
