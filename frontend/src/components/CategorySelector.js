import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  X, 
  Plus, 
  MagnifyingGlass, 
  Carrot,
  Wrench,
  Scissors,
  Horse,
  Package,
  House,
  Tree,
  Hammer,
  Palette,
  FirstAid,
  Users,
  Truck,
  PawPrint,
  Briefcase,
  Book,
  Heart,
  MagicWand,
  CaretDown,
  CaretUp,
  Check
} from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Icon mapping for categories
const CATEGORY_ICONS = {
  carrot: Carrot,
  wrench: Wrench,
  scissors: Scissors,
  cow: Horse,
  package: Package,
  house: House,
  tree: Tree,
  hammer: Hammer,
  palette: Palette,
  'first-aid': FirstAid,
  users: Users,
  tractor: Truck,
  paw: PawPrint,
  briefcase: Briefcase,
  book: Book,
  heart: Heart,
  'magic-wand': MagicWand
};

export default function CategorySelector({ 
  type, // 'goods' | 'skills' | 'services'
  mode, // 'offering' | 'wanted' (only for goods/services)
  selectedItems = [],
  onItemsChange,
  label,
  placeholder = 'Search or add custom...',
  maxDisplay = 10
}) {
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [customInput, setCustomInput] = useState('');

  useEffect(() => {
    fetchCategories();
  }, [type]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/categories/${type}`, {
        withCredentials: true
      });
      setCategories(response.data.categories || {});
    } catch (error) {
      console.error('Error fetching categories:', error);
    } finally {
      setLoading(false);
    }
  };

  // Flatten all items for search
  const allItems = useMemo(() => {
    const items = [];
    Object.entries(categories).forEach(([catKey, catData]) => {
      catData.items.forEach(item => {
        items.push({ item, category: catData.name, categoryKey: catKey });
      });
    });
    return items;
  }, [categories]);

  // Filter items based on search
  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const query = searchQuery.toLowerCase();
    return allItems.filter(({ item }) => 
      item.toLowerCase().includes(query)
    ).slice(0, 20);
  }, [searchQuery, allItems]);

  const handleSelectItem = (item) => {
    if (!selectedItems.includes(item)) {
      onItemsChange([...selectedItems, item]);
    }
    setSearchQuery('');
    setShowDropdown(false);
  };

  const handleRemoveItem = (item) => {
    onItemsChange(selectedItems.filter(i => i !== item));
  };

  const handleAddCustom = () => {
    const trimmed = customInput.trim();
    if (trimmed && !selectedItems.includes(trimmed)) {
      onItemsChange([...selectedItems, trimmed]);
      setCustomInput('');
    }
  };

  const toggleCategory = (catKey) => {
    setExpandedCategory(expandedCategory === catKey ? null : catKey);
  };

  const getCategoryIcon = (iconName) => {
    const IconComponent = CATEGORY_ICONS[iconName] || Package;
    return IconComponent;
  };

  // Color based on mode
  const accentColor = mode === 'wanted' ? '#B45309' : '#4D7C0F';
  const badgeClass = mode === 'wanted' ? 'badge-looking' : 'badge-offering';

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-[#292524] w-24 mb-2"></div>
        <div className="h-10 bg-[#292524] w-full"></div>
      </div>
    );
  }

  return (
    <div className="space-y-3" data-testid={`category-selector-${type}-${mode || 'default'}`}>
      {/* Label */}
      {label && (
        <label className="block text-xs md:text-sm mb-1.5" style={{ color: accentColor }}>
          {label}
        </label>
      )}

      {/* Search/Add Input */}
      <div className="relative">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <MagnifyingGlass 
              size={16} 
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[#78716C]" 
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              className="input-field w-full"
              style={{ paddingLeft: '2.25rem' }}
              placeholder={placeholder}
              data-testid={`category-search-${type}-${mode || 'default'}`}
            />
          </div>
        </div>

        {/* Search Results Dropdown */}
        {showDropdown && searchQuery && filteredItems.length > 0 && (
          <div className="absolute z-50 top-full left-0 right-0 mt-1 bg-[#1C1917] border border-[#44403C] max-h-60 overflow-y-auto">
            {filteredItems.map(({ item, category }, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectItem(item)}
                className={`w-full px-3 py-2 text-left text-sm flex items-center justify-between hover:bg-[#292524] transition-colors ${
                  selectedItems.includes(item) ? 'bg-[#292524]' : ''
                }`}
              >
                <span className="text-[#E7E5E4]">{item}</span>
                <span className="text-[10px] text-[#78716C]">{category}</span>
                {selectedItems.includes(item) && (
                  <Check size={14} className="text-[#4D7C0F] ml-2" />
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Custom Item Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={customInput}
          onChange={(e) => setCustomInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustom())}
          className="input-field flex-1 text-sm"
          placeholder="Add custom item..."
          data-testid={`category-custom-${type}-${mode || 'default'}`}
        />
        <button 
          type="button"
          onClick={handleAddCustom}
          className="btn-secondary px-3"
          disabled={!customInput.trim()}
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Category Browser */}
      <div className="bg-[#0C0A09] border border-[#292524] max-h-64 overflow-y-auto">
        {Object.entries(categories).map(([catKey, catData]) => {
          const IconComponent = getCategoryIcon(catData.icon);
          const isExpanded = expandedCategory === catKey;
          const selectedInCategory = catData.items.filter(item => selectedItems.includes(item));
          
          return (
            <div key={catKey} className="border-b border-[#292524] last:border-b-0">
              {/* Category Header */}
              <button
                onClick={() => toggleCategory(catKey)}
                className="w-full px-3 py-2.5 flex items-center justify-between hover:bg-[#1C1917] transition-colors"
              >
                <div className="flex items-center gap-2">
                  <IconComponent size={16} style={{ color: accentColor }} />
                  <span className="text-sm font-medium text-[#E7E5E4]">{catData.name}</span>
                  {selectedInCategory.length > 0 && (
                    <span className="text-[10px] px-1.5 py-0.5 bg-[#292524] text-[#A8A29E]">
                      {selectedInCategory.length} selected
                    </span>
                  )}
                </div>
                {isExpanded ? (
                  <CaretUp size={14} className="text-[#78716C]" />
                ) : (
                  <CaretDown size={14} className="text-[#78716C]" />
                )}
              </button>

              {/* Category Items */}
              {isExpanded && (
                <div className="px-3 pb-3 flex flex-wrap gap-1.5">
                  {catData.items.map((item, idx) => {
                    const isSelected = selectedItems.includes(item);
                    return (
                      <button
                        key={idx}
                        onClick={() => isSelected ? handleRemoveItem(item) : handleSelectItem(item)}
                        className={`text-[11px] px-2 py-1 border transition-colors ${
                          isSelected 
                            ? mode === 'wanted'
                              ? 'bg-[#B45309]/20 border-[#B45309] text-[#E7E5E4]'
                              : 'bg-[#4D7C0F]/20 border-[#4D7C0F] text-[#E7E5E4]'
                            : 'bg-transparent border-[#44403C] text-[#A8A29E] hover:border-[#78716C] hover:text-[#E7E5E4]'
                        }`}
                      >
                        {isSelected && <Check size={10} className="inline mr-1" />}
                        {item}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Selected Items Display */}
      {selectedItems.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selectedItems.slice(0, maxDisplay).map((item, idx) => (
            <span key={idx} className={`badge ${badgeClass} text-[10px] md:text-xs`}>
              {item}
              <button 
                onClick={() => handleRemoveItem(item)} 
                className="ml-1 hover:text-white"
                aria-label={`Remove ${item}`}
              >
                <X size={10} />
              </button>
            </span>
          ))}
          {selectedItems.length > maxDisplay && (
            <span className="text-xs text-[#78716C] self-center">
              +{selectedItems.length - maxDisplay} more
            </span>
          )}
        </div>
      )}

      {/* Click outside to close dropdown */}
      {showDropdown && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  );
}
