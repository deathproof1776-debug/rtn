import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  User, 
  MapPin, 
  Tag, 
  ArrowsLeftRight,
  FloppyDisk,
  Plus,
  X,
  Camera
} from '@phosphor-icons/react';

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
    avatar: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [skillInput, setSkillInput] = useState('');
  const [goodsOfferingInput, setGoodsOfferingInput] = useState('');
  const [goodsWantedInput, setGoodsWantedInput] = useState('');
  const [servicesOfferingInput, setServicesOfferingInput] = useState('');
  const [servicesWantedInput, setServicesWantedInput] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchProfile();
  }, [user]);

  const fetchProfile = async () => {
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
        avatar: response.data.avatar || ''
      });
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

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

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setProfile({ ...profile, avatar: `${API_URL}${response.data.url}` });
    } catch (error) {
      console.error('Error uploading avatar:', error);
    }
  };

  const addToArray = (field, value, setValue) => {
    if (value.trim() && !profile[field].includes(value.trim())) {
      setProfile({ ...profile, [field]: [...profile[field], value.trim()] });
      setValue('');
    }
  };

  const removeFromArray = (field, value) => {
    setProfile({ ...profile, [field]: profile[field].filter(v => v !== value) });
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
            <h3 className="text-base md:text-lg font-semibold text-[#E7E5E4] truncate">{profile.name || 'Your Name'}</h3>
            <p className="text-xs md:text-sm text-[#78716C]">Tap the camera to change avatar</p>
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

        {/* Skills */}
        <div>
          <label className="block text-xs md:text-sm text-[#A8A29E] mb-1.5 md:mb-2">
            <Tag size={12} className="inline mr-1" />
            Skills
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('skills', skillInput, setSkillInput))}
              className="input-field flex-1"
              placeholder="e.g., Woodworking"
              data-testid="skills-input"
            />
            <button 
              type="button" 
              onClick={() => addToArray('skills', skillInput, setSkillInput)} 
              className="btn-secondary px-3"
            >
              <Plus size={18} />
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 md:gap-2">
            {profile.skills.map((skill, i) => (
              <span key={i} className="tag text-xs md:text-sm">
                {skill}
                <button onClick={() => removeFromArray('skills', skill)}><X size={12} /></button>
              </span>
            ))}
          </div>
        </div>

        {/* Goods */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs md:text-sm text-[#4D7C0F] mb-1.5 md:mb-2">Goods You're Offering</label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={goodsOfferingInput}
                onChange={(e) => setGoodsOfferingInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('goods_offering', goodsOfferingInput, setGoodsOfferingInput))}
                className="input-field flex-1"
                placeholder="e.g., Eggs, Honey"
                data-testid="goods-offering-input"
              />
              <button type="button" onClick={() => addToArray('goods_offering', goodsOfferingInput, setGoodsOfferingInput)} className="btn-secondary px-3">
                <Plus size={18} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {profile.goods_offering.map((item, i) => (
                <span key={i} className="badge badge-offering text-[10px] md:text-xs">
                  {item}
                  <button onClick={() => removeFromArray('goods_offering', item)} className="ml-1"><X size={10} /></button>
                </span>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs md:text-sm text-[#B45309] mb-1.5 md:mb-2">Goods You Want</label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={goodsWantedInput}
                onChange={(e) => setGoodsWantedInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('goods_wanted', goodsWantedInput, setGoodsWantedInput))}
                className="input-field flex-1"
                placeholder="e.g., Seeds, Lumber"
                data-testid="goods-wanted-input"
              />
              <button type="button" onClick={() => addToArray('goods_wanted', goodsWantedInput, setGoodsWantedInput)} className="btn-secondary px-3">
                <Plus size={18} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {profile.goods_wanted.map((item, i) => (
                <span key={i} className="badge badge-looking text-[10px] md:text-xs">
                  {item}
                  <button onClick={() => removeFromArray('goods_wanted', item)} className="ml-1"><X size={10} /></button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Services */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs md:text-sm text-[#4D7C0F] mb-1.5 md:mb-2">Services You Offer</label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={servicesOfferingInput}
                onChange={(e) => setServicesOfferingInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('services_offering', servicesOfferingInput, setServicesOfferingInput))}
                className="input-field flex-1"
                placeholder="e.g., Carpentry"
                data-testid="services-offering-input"
              />
              <button type="button" onClick={() => addToArray('services_offering', servicesOfferingInput, setServicesOfferingInput)} className="btn-secondary px-3">
                <Plus size={18} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {profile.services_offering.map((item, i) => (
                <span key={i} className="badge badge-offering text-[10px] md:text-xs">
                  {item}
                  <button onClick={() => removeFromArray('services_offering', item)} className="ml-1"><X size={10} /></button>
                </span>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs md:text-sm text-[#B45309] mb-1.5 md:mb-2">Services You Need</label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={servicesWantedInput}
                onChange={(e) => setServicesWantedInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('services_wanted', servicesWantedInput, setServicesWantedInput))}
                className="input-field flex-1"
                placeholder="e.g., Plumbing"
                data-testid="services-wanted-input"
              />
              <button type="button" onClick={() => addToArray('services_wanted', servicesWantedInput, setServicesWantedInput)} className="btn-secondary px-3">
                <Plus size={18} />
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {profile.services_wanted.map((item, i) => (
                <span key={i} className="badge badge-looking text-[10px] md:text-xs">
                  {item}
                  <button onClick={() => removeFromArray('services_wanted', item)} className="ml-1"><X size={10} /></button>
                </span>
              ))}
            </div>
          </div>
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
    </div>
  );
}
