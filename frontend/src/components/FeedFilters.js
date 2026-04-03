/**
 * FeedFilters - Reusable filter controls for Barter Feed and Community Board
 */
import { useState } from 'react';
import { 
  Funnel, 
  MapPin, 
  Handshake, 
  SealCheck,
  CaretDown,
  X
} from '@phosphor-icons/react';

export default function FeedFilters({ 
  filters, 
  onFilterChange, 
  categories = [],
  showCategoryFilter = true,
  categoryLabel = "Category"
}) {
  const [showFilters, setShowFilters] = useState(false);
  
  const activeFilterCount = [
    filters.nearby,
    filters.network,
    filters.verified,
    filters.category && filters.category !== 'all'
  ].filter(Boolean).length;

  const handleFilterToggle = (key) => {
    onFilterChange({ ...filters, [key]: !filters[key] });
  };

  const handleCategoryChange = (category) => {
    onFilterChange({ ...filters, category });
    setShowFilters(false);
  };

  const clearFilters = () => {
    onFilterChange({
      nearby: false,
      network: false,
      verified: false,
      category: 'all'
    });
  };

  return (
    <div className="relative" data-testid="feed-filters">
      {/* Filter Toggle Button */}
      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs border transition-all ${
            activeFilterCount > 0
              ? 'bg-[var(--brand-primary)] border-[var(--brand-primary)] text-white'
              : 'bg-transparent border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--brand-primary)]'
          }`}
          data-testid="filter-toggle-btn"
        >
          <Funnel size={14} weight={activeFilterCount > 0 ? 'fill' : 'regular'} />
          <span>Filters</span>
          {activeFilterCount > 0 && (
            <span className="ml-1 px-1.5 py-0.5 bg-white/20 rounded-full text-[10px]">
              {activeFilterCount}
            </span>
          )}
          <CaretDown size={12} className={`transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>

        {/* Quick filter pills */}
        <button
          onClick={() => handleFilterToggle('nearby')}
          className={`flex items-center gap-1 px-2.5 py-1.5 text-xs border transition-all ${
            filters.nearby 
              ? 'bg-[var(--brand-accent)]/20 border-[var(--brand-accent)] text-[var(--brand-accent)]' 
              : 'bg-transparent border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--brand-accent)]'
          }`}
          data-testid="filter-nearby"
        >
          <MapPin size={12} weight={filters.nearby ? 'fill' : 'regular'} />
          <span className="hidden sm:inline">Nearby</span>
        </button>

        <button
          onClick={() => handleFilterToggle('network')}
          className={`flex items-center gap-1 px-2.5 py-1.5 text-xs border transition-all ${
            filters.network 
              ? 'bg-[var(--brand-primary)]/20 border-[var(--brand-primary)] text-[var(--brand-primary)]' 
              : 'bg-transparent border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--brand-primary)]'
          }`}
          data-testid="filter-network"
        >
          <Handshake size={12} weight={filters.network ? 'fill' : 'regular'} />
          <span className="hidden sm:inline">Network</span>
        </button>

        <button
          onClick={() => handleFilterToggle('verified')}
          className={`flex items-center gap-1 px-2.5 py-1.5 text-xs border transition-all ${
            filters.verified 
              ? 'bg-green-900/30 border-green-600 text-green-500' 
              : 'bg-transparent border-[var(--border-color)] text-[var(--text-secondary)] hover:border-green-600'
          }`}
          data-testid="filter-verified"
        >
          <SealCheck size={12} weight={filters.verified ? 'fill' : 'regular'} />
          <span className="hidden sm:inline">Verified</span>
        </button>

        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-1 px-2 py-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--brand-danger)] transition-colors"
            data-testid="clear-filters"
          >
            <X size={12} />
            Clear
          </button>
        )}
      </div>

      {/* Expanded Filter Panel */}
      {showFilters && showCategoryFilter && categories.length > 0 && (
        <div 
          className="absolute top-full left-0 mt-2 w-64 bg-[var(--bg-surface)] border border-[var(--border-color)] rounded-lg shadow-xl z-50 p-3"
          data-testid="filter-panel"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
              {categoryLabel}
            </span>
            <button 
              onClick={() => setShowFilters(false)}
              className="p-1 hover:bg-[var(--bg-surface-hover)] rounded"
            >
              <X size={14} />
            </button>
          </div>
          
          <div className="space-y-1 max-h-60 overflow-y-auto">
            <button
              onClick={() => handleCategoryChange('all')}
              className={`w-full text-left px-3 py-2 text-sm rounded transition-colors ${
                filters.category === 'all' || !filters.category
                  ? 'bg-[var(--brand-primary)]/20 text-[var(--brand-primary)]'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)]'
              }`}
            >
              All {categoryLabel}s
            </button>
            {categories.map((cat) => (
              <button
                key={cat.id || cat}
                onClick={() => handleCategoryChange(cat.id || cat)}
                className={`w-full text-left px-3 py-2 text-sm rounded transition-colors ${
                  filters.category === (cat.id || cat)
                    ? 'bg-[var(--brand-primary)]/20 text-[var(--brand-primary)]'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)]'
                }`}
              >
                {cat.name || cat}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Backdrop */}
      {showFilters && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowFilters(false)}
        />
      )}
    </div>
  );
}
