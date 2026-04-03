/**
 * FeedFilters - Enhanced filter controls for Barter Feed and Community Board
 * Includes: Search, Time Range, Sort, Has Media, Category/Topic filters
 */
import { useState } from 'react';
import { 
  Funnel, 
  MapPin, 
  Handshake, 
  SealCheck,
  CaretDown,
  X,
  MagnifyingGlass,
  Clock,
  SortAscending,
  Image as ImageIcon,
  Fire,
  Star,
  ArrowsDownUp
} from '@phosphor-icons/react';

// Time range options
const TIME_RANGES = [
  { id: 'all', label: 'All Time' },
  { id: 'today', label: 'Today' },
  { id: 'week', label: 'This Week' },
  { id: 'month', label: 'This Month' }
];

// Sort options
const SORT_OPTIONS = [
  { id: 'recent', label: 'Most Recent', icon: Clock },
  { id: 'popular', label: 'Most Popular', icon: Fire },
  { id: 'commented', label: 'Most Discussed', icon: Star }
];

export default function FeedFilters({ 
  filters, 
  onFilterChange, 
  categories = [],
  showCategoryFilter = true,
  categoryLabel = "Category",
  showSearch = true,
  showTimeFilter = true,
  showSortFilter = true,
  showMediaFilter = true
}) {
  const [showFilters, setShowFilters] = useState(false);
  const [searchInput, setSearchInput] = useState(filters.search || '');
  
  // Count active filters
  const activeFilterCount = [
    filters.nearby,
    filters.network,
    filters.verified,
    filters.hasMedia,
    filters.category && filters.category !== 'all',
    filters.timeRange && filters.timeRange !== 'all',
    filters.sortBy && filters.sortBy !== 'recent',
    filters.search && filters.search.trim()
  ].filter(Boolean).length;

  const handleFilterToggle = (key) => {
    onFilterChange({ ...filters, [key]: !filters[key] });
  };

  const handleCategoryChange = (category) => {
    onFilterChange({ ...filters, category });
  };

  const handleTimeRangeChange = (timeRange) => {
    onFilterChange({ ...filters, timeRange });
  };

  const handleSortChange = (sortBy) => {
    onFilterChange({ ...filters, sortBy });
  };

  const handleSearchSubmit = (e) => {
    e?.preventDefault();
    onFilterChange({ ...filters, search: searchInput.trim() });
  };

  const clearSearch = () => {
    setSearchInput('');
    onFilterChange({ ...filters, search: '' });
  };

  const clearFilters = () => {
    setSearchInput('');
    onFilterChange({
      nearby: false,
      network: false,
      verified: false,
      hasMedia: false,
      category: 'all',
      timeRange: 'all',
      sortBy: 'recent',
      search: ''
    });
  };

  return (
    <div className="space-y-3" data-testid="feed-filters">
      {/* Search Bar */}
      {showSearch && (
        <form onSubmit={handleSearchSubmit} className="relative">
          <MagnifyingGlass 
            size={16} 
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" 
          />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search posts..."
            className="w-full pl-9 pr-20 py-2 bg-[var(--bg-surface)] border border-[var(--border-color)] rounded text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--brand-primary)] focus:outline-none"
            data-testid="filter-search-input"
          />
          {searchInput && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-14 top-1/2 -translate-y-1/2 p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              <X size={14} />
            </button>
          )}
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 text-xs bg-[var(--brand-primary)] text-white rounded hover:bg-[var(--brand-primary-hover)] transition-colors"
            data-testid="filter-search-btn"
          >
            Search
          </button>
        </form>
      )}

      {/* Filter Row */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Advanced Filters Dropdown */}
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

        {showMediaFilter && (
          <button
            onClick={() => handleFilterToggle('hasMedia')}
            className={`flex items-center gap-1 px-2.5 py-1.5 text-xs border transition-all ${
              filters.hasMedia 
                ? 'bg-purple-900/30 border-purple-600 text-purple-400' 
                : 'bg-transparent border-[var(--border-color)] text-[var(--text-secondary)] hover:border-purple-600'
            }`}
            data-testid="filter-has-media"
          >
            <ImageIcon size={12} weight={filters.hasMedia ? 'fill' : 'regular'} />
            <span className="hidden sm:inline">Has Media</span>
          </button>
        )}

        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-1 px-2 py-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--brand-danger)] transition-colors"
            data-testid="clear-filters"
          >
            <X size={12} />
            Clear All
          </button>
        )}
      </div>

      {/* Expanded Filter Panel */}
      {showFilters && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setShowFilters(false)}
          />
          <div 
            className="absolute left-0 mt-2 w-80 bg-[var(--bg-surface)] border border-[var(--border-color)] rounded-lg shadow-xl z-50 p-4"
            data-testid="filter-panel"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-semibold text-[var(--text-primary)]">
                Advanced Filters
              </span>
              <button 
                onClick={() => setShowFilters(false)}
                className="p-1 hover:bg-[var(--bg-surface-hover)] rounded"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Category/Topic Filter */}
              {showCategoryFilter && categories.length > 0 && (
                <div>
                  <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    {categoryLabel}
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    <button
                      onClick={() => handleCategoryChange('all')}
                      className={`px-2.5 py-1 text-xs rounded transition-colors ${
                        filters.category === 'all' || !filters.category
                          ? 'bg-[var(--brand-primary)] text-white'
                          : 'bg-[var(--bg-surface-hover)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-active)]'
                      }`}
                    >
                      All
                    </button>
                    {categories.map((cat) => (
                      <button
                        key={cat.id || cat}
                        onClick={() => handleCategoryChange(cat.id || cat)}
                        className={`px-2.5 py-1 text-xs rounded transition-colors ${
                          filters.category === (cat.id || cat)
                            ? 'bg-[var(--brand-primary)] text-white'
                            : 'bg-[var(--bg-surface-hover)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-active)]'
                        }`}
                      >
                        {cat.name || cat}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Time Range Filter */}
              {showTimeFilter && (
                <div>
                  <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    <Clock size={12} className="inline mr-1" />
                    Time Range
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {TIME_RANGES.map((range) => (
                      <button
                        key={range.id}
                        onClick={() => handleTimeRangeChange(range.id)}
                        className={`px-2.5 py-1 text-xs rounded transition-colors ${
                          (filters.timeRange || 'all') === range.id
                            ? 'bg-[var(--brand-primary)] text-white'
                            : 'bg-[var(--bg-surface-hover)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-active)]'
                        }`}
                        data-testid={`filter-time-${range.id}`}
                      >
                        {range.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Sort Filter */}
              {showSortFilter && (
                <div>
                  <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    <ArrowsDownUp size={12} className="inline mr-1" />
                    Sort By
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {SORT_OPTIONS.map((option) => {
                      const Icon = option.icon;
                      return (
                        <button
                          key={option.id}
                          onClick={() => handleSortChange(option.id)}
                          className={`flex items-center gap-1 px-2.5 py-1 text-xs rounded transition-colors ${
                            (filters.sortBy || 'recent') === option.id
                              ? 'bg-[var(--brand-primary)] text-white'
                              : 'bg-[var(--bg-surface-hover)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-active)]'
                          }`}
                          data-testid={`filter-sort-${option.id}`}
                        >
                          <Icon size={12} />
                          {option.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Quick Toggles Summary */}
              <div className="pt-3 border-t border-[var(--border-color)]">
                <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                  Quick Filters
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.nearby || false}
                      onChange={() => handleFilterToggle('nearby')}
                      className="w-4 h-4 accent-[var(--brand-primary)]"
                    />
                    <span className="text-xs text-[var(--text-secondary)]">Nearby Only</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.network || false}
                      onChange={() => handleFilterToggle('network')}
                      className="w-4 h-4 accent-[var(--brand-primary)]"
                    />
                    <span className="text-xs text-[var(--text-secondary)]">My Network</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.verified || false}
                      onChange={() => handleFilterToggle('verified')}
                      className="w-4 h-4 accent-[var(--brand-primary)]"
                    />
                    <span className="text-xs text-[var(--text-secondary)]">Verified Only</span>
                  </label>
                  {showMediaFilter && (
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.hasMedia || false}
                        onChange={() => handleFilterToggle('hasMedia')}
                        className="w-4 h-4 accent-[var(--brand-primary)]"
                      />
                      <span className="text-xs text-[var(--text-secondary)]">Has Media</span>
                    </label>
                  )}
                </div>
              </div>
            </div>

            {/* Apply/Clear Buttons */}
            <div className="flex gap-2 mt-4 pt-3 border-t border-[var(--border-color)]">
              <button
                onClick={clearFilters}
                className="flex-1 px-3 py-2 text-xs text-[var(--text-secondary)] border border-[var(--border-color)] rounded hover:bg-[var(--bg-surface-hover)] transition-colors"
              >
                Clear All
              </button>
              <button
                onClick={() => setShowFilters(false)}
                className="flex-1 px-3 py-2 text-xs bg-[var(--brand-primary)] text-white rounded hover:bg-[var(--brand-primary-hover)] transition-colors"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
