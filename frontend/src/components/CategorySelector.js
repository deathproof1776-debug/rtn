import { useState, useEffect, useMemo, useCallback } from 'react';
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
  Check,
  PencilSimple,
  Info
} from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Helper to normalize item to object format
const normalizeItem = (item) => {
  if (typeof item === 'string') {
    return { name: item, description: '', quantity: '' };
  }
  return { name: item.name || '', description: item.description || '', quantity: item.quantity || '' };
};

// Helper to get item name regardless of format
const getItemName = (item) => {
  if (typeof item === 'string') return item;
  return item?.name || '';
};

// Helper to check if an item name is in the selected list
const isItemSelected = (selectedItems, itemName) => {
  return selectedItems.some(selected => getItemName(selected) === itemName);
};

// Icon mapping for categories

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
  const [editingItem, setEditingItem] = useState(null); // Track which item is being edited
  const [editDescription, setEditDescription] = useState('');
  const [editQuantity, setEditQuantity] = useState('');

  const fetchCategories = useCallback(async () => {
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
  }, [type]);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

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

  const handleSelectItem = (itemName) => {
    if (!isItemSelected(selectedItems, itemName)) {
      // Add as object with empty description/quantity
      onItemsChange([...selectedItems, { name: itemName, description: '', quantity: '' }]);
    }
    setSearchQuery('');
    setShowDropdown(false);
  };

  const handleRemoveItem = (itemName) => {
    onItemsChange(selectedItems.filter(i => getItemName(i) !== itemName));
    if (editingItem === itemName) {
      setEditingItem(null);
    }
  };

  const handleAddCustom = () => {
    const trimmed = customInput.trim();
    if (trimmed && !isItemSelected(selectedItems, trimmed)) {
      onItemsChange([...selectedItems, { name: trimmed, description: '', quantity: '' }]);
      setCustomInput('');
    }
  };

  const handleEditItem = (itemName) => {
    const item = selectedItems.find(i => getItemName(i) === itemName);
    if (item) {
      const normalized = normalizeItem(item);
      setEditingItem(itemName);
      setEditDescription(normalized.description);
      setEditQuantity(normalized.quantity);
    }
  };

  const handleSaveItemDetails = (itemName) => {
    const updatedItems = selectedItems.map(item => {
      if (getItemName(item) === itemName) {
        return { name: itemName, description: editDescription, quantity: editQuantity };
      }
      return normalizeItem(item);
    });
    onItemsChange(updatedItems);
    setEditingItem(null);
    setEditDescription('');
    setEditQuantity('');
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
            {filteredItems.map(({ item, category }, idx) => {
              const isSelected = isItemSelected(selectedItems, item);
              return (
                <button
                  key={`search-${item}-${category}`}
                  onClick={() => handleSelectItem(item)}
                  className={`w-full px-3 py-2 text-left text-sm flex items-center justify-between hover:bg-[#292524] transition-colors ${
                    isSelected ? 'bg-[#292524]' : ''
                  }`}
                >
                  <span className="text-[#E7E5E4]">{item}</span>
                  <span className="text-[10px] text-[#78716C]">{category}</span>
                  {isSelected && (
                    <Check size={14} className="text-[#4D7C0F] ml-2" />
                  )}
                </button>
              );
            })}
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
          const selectedInCategory = catData.items.filter(item => isItemSelected(selectedItems, item));
          
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
                    const isSelected = isItemSelected(selectedItems, item);
                    return (
                      <button
                        key={`cat-item-${category}-${item}`}
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

      {/* Selected Items Display with Edit Capability */}
      {selectedItems.length > 0 && (
        <div className="space-y-2">
          {selectedItems.slice(0, maxDisplay).map((item, idx) => {
            const normalizedItem = normalizeItem(item);
            const itemName = normalizedItem.name;
            const hasDetails = normalizedItem.description || normalizedItem.quantity;
            const isEditing = editingItem === itemName;
            
            return (
              <div key={`selected-${itemName}-${idx}`} className="bg-[#0C0A09] border border-[#292524] p-2">
                <div className="flex items-center justify-between gap-2">
                  <span className={`badge ${badgeClass} text-[10px] md:text-xs`}>
                    {itemName}
                    {normalizedItem.quantity && (
                      <span className="ml-1 opacity-75">({normalizedItem.quantity})</span>
                    )}
                  </span>
                  <div className="flex items-center gap-1">
                    <button 
                      onClick={() => isEditing ? handleSaveItemDetails(itemName) : handleEditItem(itemName)}
                      className="p-1 text-[#78716C] hover:text-[#B45309] transition-colors"
                      title={isEditing ? "Save details" : "Add details"}
                    >
                      {isEditing ? <Check size={14} /> : <PencilSimple size={14} />}
                    </button>
                    <button 
                      onClick={() => handleRemoveItem(itemName)} 
                      className="p-1 text-[#78716C] hover:text-[#991B1B] transition-colors"
                      aria-label={`Remove ${itemName}`}
                    >
                      <X size={14} />
                    </button>
                  </div>
                </div>
                
                {/* Description & Quantity display */}
                {!isEditing && hasDetails && (
                  <div className="mt-1.5 text-[10px] text-[#A8A29E] flex items-start gap-1">
                    <Info size={12} className="flex-shrink-0 mt-0.5" />
                    <span>{normalizedItem.description}</span>
                  </div>
                )}
                
                {/* Edit form */}
                {isEditing && (
                  <div className="mt-2 space-y-2">
                    <div>
                      <label className="block text-[10px] text-[#78716C] mb-1">Quantity (optional)</label>
                      <input
                        type="text"
                        value={editQuantity}
                        onChange={(e) => setEditQuantity(e.target.value)}
                        className="input-field w-full text-xs py-1.5"
                        placeholder="e.g., 2 dozen/week, 5 lbs, 10 hours"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-[#78716C] mb-1">Description (optional)</label>
                      <input
                        type="text"
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        className="input-field w-full text-xs py-1.5"
                        placeholder="e.g., Free range, Organic, 10 years experience"
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          {selectedItems.length > maxDisplay && (
            <span className="text-xs text-[#78716C]">
              +{selectedItems.length - maxDisplay} more items
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
