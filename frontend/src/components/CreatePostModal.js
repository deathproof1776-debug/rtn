import { useState, useRef } from 'react';
import { X, Plus, Image, Tag, ArrowsLeftRight, PencilSimple, Check } from '@phosphor-icons/react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORIES = [
  { value: 'goods', label: 'Goods' },
  { value: 'services', label: 'Services' },
  { value: 'skills', label: 'Skills' },
];

// Helper to get item name
const getItemName = (item) => typeof item === 'string' ? item : item?.name || '';

export default function CreatePostModal({ onClose, onPostCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('goods');
  const [offering, setOffering] = useState([]);  // Array of {name, description, quantity}
  const [offeringInput, setOfferingInput] = useState('');
  const [lookingFor, setLookingFor] = useState([]);
  const [lookingForInput, setLookingForInput] = useState('');
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  
  // Item detail editing state
  const [editingItem, setEditingItem] = useState(null); // {type: 'offering'|'lookingFor', index: number}
  const [editQuantity, setEditQuantity] = useState('');
  const [editItemDescription, setEditItemDescription] = useState('');

  const handleAddOffering = () => {
    const trimmed = offeringInput.trim();
    if (trimmed && !offering.some(o => getItemName(o) === trimmed)) {
      setOffering([...offering, { name: trimmed, description: '', quantity: '' }]);
      setOfferingInput('');
    }
  };

  const handleAddLookingFor = () => {
    const trimmed = lookingForInput.trim();
    if (trimmed && !lookingFor.some(l => getItemName(l) === trimmed)) {
      setLookingFor([...lookingFor, { name: trimmed, description: '', quantity: '' }]);
      setLookingForInput('');
    }
  };

  const handleRemoveOffering = (index) => {
    setOffering(offering.filter((_, i) => i !== index));
    if (editingItem?.type === 'offering' && editingItem?.index === index) {
      setEditingItem(null);
    }
  };

  const handleRemoveLookingFor = (index) => {
    setLookingFor(lookingFor.filter((_, i) => i !== index));
    if (editingItem?.type === 'lookingFor' && editingItem?.index === index) {
      setEditingItem(null);
    }
  };

  const handleEditItem = (type, index) => {
    const item = type === 'offering' ? offering[index] : lookingFor[index];
    setEditingItem({ type, index });
    setEditQuantity(item.quantity || '');
    setEditItemDescription(item.description || '');
  };

  const handleSaveItemDetails = () => {
    if (!editingItem) return;
    
    if (editingItem.type === 'offering') {
      const updated = [...offering];
      updated[editingItem.index] = {
        ...updated[editingItem.index],
        quantity: editQuantity,
        description: editItemDescription
      };
      setOffering(updated);
    } else {
      const updated = [...lookingFor];
      updated[editingItem.index] = {
        ...updated[editingItem.index],
        quantity: editQuantity,
        description: editItemDescription
      };
      setLookingFor(updated);
    }
    
    setEditingItem(null);
    setEditQuantity('');
    setEditItemDescription('');
  };

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
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" data-testid="create-post-modal">
      <div className="bg-[#1C1917] border border-[#292524] w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <div className="flex items-center justify-between p-4 border-b border-[#292524]">
          <h2 className="text-xl font-bold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Create Barter Post
          </h2>
          <button onClick={onClose} className="btn-ghost p-2" data-testid="close-modal">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="bg-[#991B1B]/20 border border-[#991B1B] text-[#E7E5E4] px-4 py-3">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-[#A8A29E] mb-2">Title</label>
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
            <label className="block text-sm text-[#A8A29E] mb-2">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input-field w-full h-24 resize-none"
              placeholder="Describe what you have and what you're looking for..."
              data-testid="post-description-input"
            />
          </div>

          <div>
            <label className="block text-sm text-[#A8A29E] mb-2">Category</label>
            <div className="flex gap-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => setCategory(cat.value)}
                  className={`px-4 py-2 border ${
                    category === cat.value 
                      ? 'bg-[#B45309] border-[#B45309] text-[#E7E5E4]' 
                      : 'bg-[#0C0A09] border-[#44403C] text-[#A8A29E]'
                  }`}
                  data-testid={`category-${cat.value}`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm text-[#A8A29E] mb-2">
              <Tag size={16} className="inline mr-1 text-[#4D7C0F]" />
              What You're Offering
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={offeringInput}
                onChange={(e) => setOfferingInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddOffering())}
                className="input-field flex-1"
                placeholder="e.g., Fresh eggs, Woodworking"
                data-testid="offering-input"
              />
              <button type="button" onClick={handleAddOffering} className="btn-secondary px-3">
                <Plus size={20} />
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {offering.map((item, i) => {
                const isEditing = editingItem?.type === 'offering' && editingItem?.index === i;
                return (
                  <div key={`offering-${item.name}-${i}`} className="bg-[#0C0A09] border border-[#292524] p-2 flex-shrink-0">
                    <div className="flex items-center gap-2">
                      <span className="tag m-0">
                        {item.name}
                        {item.quantity && <span className="ml-1 opacity-75">({item.quantity})</span>}
                      </span>
                      <button 
                        type="button" 
                        onClick={() => isEditing ? handleSaveItemDetails() : handleEditItem('offering', i)}
                        className="text-[#78716C] hover:text-[#B45309]"
                        title={isEditing ? "Save" : "Add details"}
                      >
                        {isEditing ? <Check size={14} /> : <PencilSimple size={14} />}
                      </button>
                      <button type="button" onClick={() => handleRemoveOffering(i)} className="text-[#78716C] hover:text-[#991B1B]">
                        <X size={14} />
                      </button>
                    </div>
                    {isEditing && (
                      <div className="mt-2 space-y-2">
                        <input
                          type="text"
                          value={editQuantity}
                          onChange={(e) => setEditQuantity(e.target.value)}
                          className="input-field w-full text-xs py-1"
                          placeholder="Qty: e.g., 2 dozen, 5 lbs"
                        />
                        <input
                          type="text"
                          value={editItemDescription}
                          onChange={(e) => setEditItemDescription(e.target.value)}
                          className="input-field w-full text-xs py-1"
                          placeholder="Details: e.g., Free range, Organic"
                        />
                      </div>
                    )}
                    {!isEditing && item.description && (
                      <div className="text-[10px] text-[#78716C] mt-1">{item.description}</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-sm text-[#A8A29E] mb-2">
              <ArrowsLeftRight size={16} className="inline mr-1 text-[#B45309]" />
              What You're Looking For
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={lookingForInput}
                onChange={(e) => setLookingForInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddLookingFor())}
                className="input-field flex-1"
                placeholder="e.g., Vegetables, Carpentry skills"
                data-testid="looking-for-input"
              />
              <button type="button" onClick={handleAddLookingFor} className="btn-secondary px-3">
                <Plus size={20} />
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {lookingFor.map((item, i) => {
                const isEditing = editingItem?.type === 'lookingFor' && editingItem?.index === i;
                return (
                  <div key={`lookingFor-${item.name}-${i}`} className="bg-[#0C0A09] border border-[#292524] p-2 flex-shrink-0">
                    <div className="flex items-center gap-2">
                      <span className="tag m-0">
                        {item.name}
                        {item.quantity && <span className="ml-1 opacity-75">({item.quantity})</span>}
                      </span>
                      <button 
                        type="button" 
                        onClick={() => isEditing ? handleSaveItemDetails() : handleEditItem('lookingFor', i)}
                        className="text-[#78716C] hover:text-[#B45309]"
                        title={isEditing ? "Save" : "Add details"}
                      >
                        {isEditing ? <Check size={14} /> : <PencilSimple size={14} />}
                      </button>
                      <button type="button" onClick={() => handleRemoveLookingFor(i)} className="text-[#78716C] hover:text-[#991B1B]">
                        <X size={14} />
                      </button>
                    </div>
                    {isEditing && (
                      <div className="mt-2 space-y-2">
                        <input
                          type="text"
                          value={editQuantity}
                          onChange={(e) => setEditQuantity(e.target.value)}
                          className="input-field w-full text-xs py-1"
                          placeholder="Qty: e.g., 2 dozen, 5 lbs"
                        />
                        <input
                          type="text"
                          value={editItemDescription}
                          onChange={(e) => setEditItemDescription(e.target.value)}
                          className="input-field w-full text-xs py-1"
                          placeholder="Details: e.g., Preferably organic"
                        />
                      </div>
                    )}
                    {!isEditing && item.description && (
                      <div className="text-[10px] text-[#78716C] mt-1">{item.description}</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-sm text-[#A8A29E] mb-2">
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
                    <img src={img} alt="" className="w-full h-20 object-cover border border-[#292524]" />
                    <button
                      type="button"
                      onClick={() => setImages(images.filter((_, idx) => idx !== i))}
                      className="absolute -top-2 -right-2 w-5 h-5 bg-[#991B1B] flex items-center justify-center"
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
              {loading ? 'Creating...' : 'Create Post'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
