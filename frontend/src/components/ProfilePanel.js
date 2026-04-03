import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  User, 
  MapPin, 
  FloppyDisk,
  Camera,
  SealCheck,
  Handshake,
  Carrot,
  Wrench,
  Briefcase,
  Images
} from '@phosphor-icons/react';
import CategorySelector from './CategorySelector';
import Gallery from './Gallery';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ProfilePanel() {
  const { user, updateUser } = useAuth();
  const [profile, setProfile] = useState({
    name: '',
    location: '',
    bio: '',
    skills: [],
    goods_offering: [],
    goods_wanted: [],
    services_offering: [],
    services_wanted: [],
    avatar: '',
    is_verified: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [networkConnections, setNetworkConnections] = useState([]);
  const [showGallery, setShowGallery] = useState(false);
  const fileInputRef = useRef(null);

  const fetchProfile = useCallback(async () => {
    if (!user?.id) return;
    try {
      const response = await axios.get(`${API_URL}/api/profile/${user.id}`, {
        withCredentials: true
      });
      setProfile({
        name: response.data.name || '',
        location: response.data.location || '',
        bio: response.data.bio || '',
        skills: response.data.skills || [],
        goods_offering: response.data.goods_offering || [],
        goods_wanted: response.data.goods_wanted || [],
        services_offering: response.data.services_offering || [],
        services_wanted: response.data.services_wanted || [],
        avatar: response.data.avatar || '',
        is_verified: response.data.is_verified || false
      });
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const fetchNetworkConnections = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/network/connections`, {
        withCredentials: true
      });
      setNetworkConnections(response.data.connections || []);
    } catch (error) {
      console.error('Error fetching network connections:', error);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
    fetchNetworkConnections();
  }, [fetchProfile, fetchNetworkConnections]);

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      await axios.put(`${API_URL}/api/profile`, profile, {
        withCredentials: true
      });
      updateUser({ name: profile.name, location: profile.location });
      setMessage('Profile saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error saving profile');
      console.error('Error saving profile:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a valid image file (JPEG, PNG, GIF, or WebP)');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      alert('Image too large. Maximum size is 10MB');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', 'avatar');

    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setProfile({ ...profile, avatar: `${API_URL}${response.data.url}` });
    } catch (error) {
      console.error('Error uploading avatar:', error);
      alert(error.response?.data?.detail || 'Failed to upload avatar');
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-[#78716C]">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto" data-testid="profile-panel">
      <div className="flex items-center gap-2 mb-4 md:mb-6">
        <User size={22} weight="duotone" className="text-[#B45309]" />
        <h2 className="text-xl md:text-2xl font-bold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Your Profile
        </h2>
      </div>

      {message && (
        <div className={`mb-4 px-3 md:px-4 py-2.5 md:py-3 text-sm ${message.includes('Error') ? 'bg-[#991B1B]/20 border border-[#991B1B]' : 'bg-[#15803D]/20 border border-[#15803D]'} text-[#E7E5E4]`}>
          {message}
        </div>
      )}

      <div className="bg-[#1C1917] border border-[#292524] p-4 md:p-6 space-y-5 md:space-y-6">
        {/* Avatar */}
        <div className="flex items-center gap-3 md:gap-4">
          <div className="relative">
            <div className="w-16 h-16 md:w-20 md:h-20 bg-[#292524] flex items-center justify-center text-[#B45309] text-xl md:text-2xl font-bold overflow-hidden flex-shrink-0">
              {profile.avatar ? (
                <img src={profile.avatar} alt="Avatar" className="w-full h-full object-cover" />
              ) : (
                profile.name?.charAt(0)?.toUpperCase() || 'U'
              )}
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="absolute -bottom-1 -right-1 md:-bottom-2 md:-right-2 w-7 h-7 md:w-8 md:h-8 bg-[#B45309] flex items-center justify-center"
            >
              <Camera size={14} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarUpload}
              className="hidden"
            />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-base md:text-lg font-semibold text-[#E7E5E4] truncate">{profile.name || 'Your Name'}</h3>
              {profile.is_verified && (
                <span className="verified-badge verified-badge-lg" data-testid="profile-verified-badge">
                  <SealCheck size={12} weight="fill" />
                  Verified Trader
                </span>
              )}
            </div>
            <p className="text-xs md:text-sm text-[#78716C]">Tap the camera to change avatar</p>
            <button
              onClick={() => setShowGallery(true)}
              className="mt-2 flex items-center gap-1.5 text-xs text-[#B45309] hover:text-[#D97706] transition-colors"
              data-testid="view-my-gallery-btn"
            >
              <Images size={14} />
              My Gallery
            </button>
          </div>
        </div>

        {/* Basic Info */}
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-xs md:text-sm text-[#A8A29E] mb-1.5 md:mb-2">Name</label>
            <input
              type="text"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              className="input-field w-full"
              data-testid="profile-name-input"
            />
          </div>
          <div>
            <label className="block text-xs md:text-sm text-[#A8A29E] mb-1.5 md:mb-2">
              <MapPin size={12} className="inline mr-1" />
              Location
            </label>
            <input
              type="text"
              value={profile.location}
              onChange={(e) => setProfile({ ...profile, location: e.target.value })}
              className="input-field w-full"
              placeholder="e.g., Rural Oregon"
              data-testid="profile-location-input"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs md:text-sm text-[#A8A29E] mb-1.5 md:mb-2">Bio</label>
          <textarea
            value={profile.bio}
            onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
            className="input-field w-full h-20 md:h-24 resize-none"
            placeholder="Tell others about yourself..."
            data-testid="profile-bio-input"
          />
        </div>

        {/* Skills Section */}
        <div className="border-t border-[#292524] pt-5">
          <div className="flex items-center gap-2 mb-4">
            <Wrench size={18} className="text-[#B45309]" />
            <h3 className="text-base font-semibold text-[#E7E5E4]">Skills</h3>
          </div>
          <CategorySelector
            type="skills"
            selectedItems={profile.skills}
            onItemsChange={(items) => setProfile({ ...profile, skills: items })}
            label="Your Skills & Expertise"
            placeholder="Search skills..."
          />
        </div>

        {/* Goods Section */}
        <div className="border-t border-[#292524] pt-5">
          <div className="flex items-center gap-2 mb-4">
            <Carrot size={18} className="text-[#B45309]" />
            <h3 className="text-base font-semibold text-[#E7E5E4]">Goods</h3>
          </div>
          
          <div className="space-y-4">
            <CategorySelector
              type="goods"
              mode="offering"
              selectedItems={profile.goods_offering}
              onItemsChange={(items) => setProfile({ ...profile, goods_offering: items })}
              label="Goods You're Offering"
              placeholder="Search goods to offer..."
            />
            
            <CategorySelector
              type="goods"
              mode="wanted"
              selectedItems={profile.goods_wanted}
              onItemsChange={(items) => setProfile({ ...profile, goods_wanted: items })}
              label="Goods You Want"
              placeholder="Search goods you need..."
            />
          </div>
        </div>

        {/* Services Section */}
        <div className="border-t border-[#292524] pt-5">
          <div className="flex items-center gap-2 mb-4">
            <Briefcase size={18} className="text-[#B45309]" />
            <h3 className="text-base font-semibold text-[#E7E5E4]">Services</h3>
          </div>
          
          <div className="space-y-4">
            <CategorySelector
              type="services"
              mode="offering"
              selectedItems={profile.services_offering}
              onItemsChange={(items) => setProfile({ ...profile, services_offering: items })}
              label="Services You Offer"
              placeholder="Search services to offer..."
            />
            
            <CategorySelector
              type="services"
              mode="wanted"
              selectedItems={profile.services_wanted}
              onItemsChange={(items) => setProfile({ ...profile, services_wanted: items })}
              label="Services You Need"
              placeholder="Search services you need..."
            />
          </div>
        </div>

        {/* My Trade Network Summary */}
        <div className="bg-[#0C0A09] p-4 border border-[#292524]">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Handshake size={18} className="text-[#B45309]" />
              <span className="text-sm font-semibold text-[#E7E5E4]">My Trade Network</span>
            </div>
            <span className="text-xs text-[#78716C]">{networkConnections.length} connections</span>
          </div>
          {networkConnections.length === 0 ? (
            <p className="text-xs text-[#78716C]">
              Build your network by connecting with other traders
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {networkConnections.slice(0, 6).map((conn) => (
                <div 
                  key={conn.id} 
                  className="flex items-center gap-1.5 px-2 py-1 bg-[#1C1917] border border-[#292524]"
                  title={conn.name}
                >
                  <div className="w-5 h-5 bg-[#292524] flex items-center justify-center text-[#B45309] text-[10px] font-semibold">
                    {conn.avatar ? (
                      <img src={conn.avatar} alt="" className="w-full h-full object-cover" />
                    ) : (
                      conn.name?.charAt(0)?.toUpperCase() || 'U'
                    )}
                  </div>
                  <span className="text-xs text-[#A8A29E] truncate max-w-[80px]">{conn.name}</span>
                  {conn.is_verified && <SealCheck size={10} className="text-[#B45309] flex-shrink-0" weight="fill" />}
                </div>
              ))}
              {networkConnections.length > 6 && (
                <span className="text-xs text-[#78716C] self-center">+{networkConnections.length - 6} more</span>
              )}
            </div>
          )}
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary w-full flex items-center justify-center gap-2"
          data-testid="save-profile-button"
        >
          <FloppyDisk size={18} weight="fill" />
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </div>

      {/* Gallery Modal */}
      {showGallery && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <div className="bg-[#1C1917] rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            <Gallery 
              userId={user?.id}
              isOwnProfile={true}
              onBack={() => setShowGallery(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
