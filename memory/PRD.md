# Rebel Trade Network - Bartering Platform

## Original Problem Statement
Social media platform for homesteaders, survivalists, and those exiting corporate control. Features Facebook aesthetics with LinkedIn functionality. Profiles include location, skills, goods/services for barter. Photo/video uploads, direct messaging, main feed with matching algorithm. Full encryption.

## User Choices
- JWT-based custom auth (email/password)
- Local file storage for photos/videos
- Full encryption (messages + all user data)
- WebSocket-based real-time chat
- Rebel homesteader vibe aesthetic with orange accents
- Push notifications for all activity (messages, comments, likes, matches)
- Trade Network feature (LinkedIn-style mutual connections)
- Recommended Traders feature (complementary goods/services matching)
- **Categorized Goods/Skills/Services** with predefined options + custom entries
- **Light/Dark Mode** with soft earth tones in light mode

## Architecture
- **Backend**: FastAPI + MongoDB + WebSocket + pywebpush
  - **Modular Routes Structure** (Refactored April 3, 2026):
    - server.py (~200 lines) - Entry point, WebSocket, startup
    - routes/__init__.py - Route aggregator
    - routes/auth.py - Authentication endpoints
    - routes/posts.py - Posts and comments
    - routes/network.py - Trade network connections
    - routes/trades.py - Trade deals
    - routes/gallery.py - Gallery uploads
    - routes/profile.py - User profiles + nearby users
    - routes/admin.py - Admin dashboard
    - routes/categories.py - Category data
    - routes/invites.py - Invite system
    - routes/messaging.py - Direct messages
    - routes/notifications.py - Push notifications
    - routes/uploads.py - File uploads
    - database.py - MongoDB connection and encryption
    - auth.py - Auth helpers (JWT, password hashing)
    - models.py - Pydantic models
    - websocket_manager.py - WebSocket connection manager
    - notifications.py - Push notification helpers
    - categories.py - Predefined category data
- **Frontend**: React + Tailwind + Phosphor Icons + Service Worker
  - **Modular Components** (Refactored April 3, 2026):
    - Feed.js - Refactored to use PostCard component
    - PostCard.js - Extracted from Feed.js for modularity
    - TradeNetworkPanel.js (301 lines) - Uses network/ subcomponents
    - TradeDealsPanel.js (235 lines) - Uses trades/ subcomponents
    - CommunityBoard.js (221 lines) - Uses community/ subcomponents
    - components/network/ - RecommendedTraderCard, ConnectionCard, RequestCard
    - components/trades/ - TradeCard, HistoryCard, EmptyState
    - components/community/ - CreateCommunityPostModal
- **Auth**: JWT with httpOnly cookies
- **Encryption**: Fernet symmetric encryption for sensitive data
- **Storage**: Emergent Cloud Object Storage (persistent)
- **Push Notifications**: Web Push API with VAPID keys
- **Theming**: CSS Variables for Light/Dark mode support

## What's Been Implemented
- [x] User registration and login with JWT
- [x] Profile management (skills, goods, services, location)
- [x] Barter post creation with categories (goods/services/skills)
- [x] Main feed with posts display
- [x] Post liking functionality
- [x] Direct messaging system
- [x] Conversation management
- [x] File/image upload
- [x] User search functionality
- [x] Data encryption (location, bio, messages, post descriptions)
- [x] Rebel homesteader dark theme UI
- [x] Responsive 3-column layout
- [x] Comments on posts - Full CRUD with encryption
- [x] Location-based matching - Nearby badges, location prioritization
- [x] Push Notifications - Browser push for messages, comments, likes
- [x] Mobile UI Optimization - Bottom nav, mobile header, slide-out sidebar
- [x] Pull-to-Refresh - Native-feeling pull-down refresh on mobile feed
- [x] Rebranding to "Rebel Trade Network" - Updated all branding
- [x] Orange Borders/Trim - Added orange accent borders throughout
- [x] Verified Trader Badge System - Admin verification with badges
- [x] Trade Network Feature - LinkedIn-style mutual connections
- [x] Recommended Traders Feature - Smart trader suggestions
- [x] Categorized Goods/Skills/Services
- [x] Light/Dark Mode Theme Toggle
- [x] Invite-Only Registration System
- [x] Search Input Padding Fix
- [x] Admin Dashboard with Overview, Users, Posts, Activity Log tabs
- [x] **Trade Deals Feature** (April 2, 2026):
  - Create formal trade offers/proposals between users
  - Accept, decline, counter-offer, and cancel trade deals
  - Incoming/Outgoing/History tabs in Trade Deals panel
  - Counter-offer chain with full history display
  - Trade history private to current user only
  - "Propose Trade" button on feed post cards and user profiles
  - Real-time WebSocket + push notifications for trade activity
  - Encrypted trade messages
  - Badge count for active incoming trades on sidebar nav

- [x] **Terms of Service Feature** (April 2, 2026):
  - New users must accept Community Guidelines & Terms before registering
  - Checkbox with link to full terms modal
  - Modal covers: No illegal sales, no weapons trafficking, no harassment, 
    no threats/violence, no hate speech, full liability disclaimer
  - Submit button disabled until terms accepted
- [x] **Theme Toggle UI Fix** (April 2, 2026):
  - Fixed hardcoded colors in MessagesPanel.js and TradeNetworkPanel.js
  - Added theme-aware CSS utility classes (theme-surface, theme-surface-hover, etc.)
  - Light mode now displays correctly with soft earth tones across all components
- [x] **Enhanced PWA Features** (April 2, 2026):
  - PWA manifest with app metadata, icons, splash screen config
  - Enhanced Service Worker with caching and offline fallback page
  - "Install App" button in sidebar (iOS instructions modal included)
  - PWAContext for install state management
  - Service Worker registration on page load

## API Endpoints

### Trade Deals
- POST /api/trades (create trade offer)
- GET /api/trades/incoming (incoming offers)
- GET /api/trades/outgoing (outgoing offers)
- GET /api/trades/history (completed/declined/cancelled - current user only)
- GET /api/trades/active-count (badge count)
- POST /api/trades/{trade_id}/respond (accept/decline)
- POST /api/trades/{trade_id}/counter (counter-offer)
- POST /api/trades/{trade_id}/cancel (cancel trade)

### Admin
- POST /api/admin/verify-trader (requires admin role)
- GET /api/admin/users (requires admin role)
- GET /api/admin/stats (requires admin role)
- GET /api/admin/posts (requires admin role)
- DELETE /api/admin/posts/{post_id} (requires admin role)
- PUT /api/admin/users/{user_id}/role (requires admin role)
- DELETE /api/admin/users/{user_id} (requires admin role)
- GET /api/admin/audit-log (requires admin role)

### Categories
- GET /api/categories/all
- GET /api/categories/goods
- GET /api/categories/skills
- GET /api/categories/services

### Invites
- POST /api/invites/create
- GET /api/invites/validate/{token}
- GET /api/invites/my-invites

### Auth
- POST /api/auth/register (requires invite_token)
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/refresh

### Trade Network
- POST /api/network/request
- POST /api/network/respond
- GET /api/network/requests/pending
- GET /api/network/connections
- DELETE /api/network/connections/{user_id}
- GET /api/network/status/{user_id}
- POST /api/network/cancel/{request_id}
- GET /api/network/recommended

### Profile
- PUT /api/profile
- GET /api/profile/{user_id}

### Posts
- POST /api/posts
- GET /api/posts
- GET /api/posts/matches
- POST /api/posts/{id}/like

### Comments
- POST /api/posts/{post_id}/comments
- GET /api/posts/{post_id}/comments
- DELETE /api/posts/{post_id}/comments/{comment_id}

### Messages
- GET /api/conversations
- POST /api/messages
- GET /api/messages/{user_id}

### Users
- GET /api/users/nearby
- GET /api/users/search

### Push Notifications
- GET /api/notifications/vapid-public-key
- POST /api/notifications/subscribe
- POST /api/notifications/unsubscribe
- GET /api/notifications/status
- POST /api/notifications/test

### Other
- POST /api/upload
- WebSocket: /ws/{user_id}

## Prioritized Backlog

### P1 (High Priority)
- User blocking/reporting

### P2 (Medium Priority)
- Location radius settings (specify travel/trade distance)

### P3 (Enhancement)
- Trade ratings/reviews after completed trades

## What Was Completed (April 3, 2026)
- [x] **Backend Refactoring** - Modular routes structure
  - Reduced server.py from 3,137 lines to ~200 lines
  - Created /routes/ directory with 12 modular route files
  - Created separate modules: database.py, auth.py, models.py, websocket_manager.py, notifications.py, categories.py
  - All API endpoints preserved and working (36/36 tests pass)
  - Fixed get_recommended_traders TypeError with dict items
  - Added missing /api/users/nearby endpoint
- [x] **Frontend Refactoring** - Component modularization (Session 2)
  - TradeNetworkPanel.js: 492 → 301 lines (39% reduction)
  - TradeDealsPanel.js: 489 → 235 lines (52% reduction)
  - CommunityBoard.js: 450 → 221 lines (51% reduction)
  - Extracted to /components/network/: RecommendedTraderCard, ConnectionCard, RequestCard
  - Extracted to /components/trades/: TradeCard, HistoryCard, EmptyState
  - Extracted to /components/community/: CreateCommunityPostModal
  - All components verified working via testing agent (32/32 backend tests, 100% frontend pass)
- [x] **Frontend Refactoring** - Component modularization (Session 1)
  - Extracted PostCard.js from Feed.js for better reusability
  - Feed.js reduced from 554 lines to ~170 lines
- [x] **Community Board** - New general discussion forum
  - 15 topic categories (Homesteading, Off-Grid, Prepping, DIY, Gardening, Livestock, Food Preservation, Energy, Water, Security, Health, Finance, Community, News, General)
  - Full media support (images)
  - Likes, threaded comments, topic badges
  - /api/community/* endpoints
- [x] **Admin System Messages** - Scrolling banner announcements
  - Create, edit, toggle active, delete messages
  - 4 message types: Info (blue), Warning (yellow), Success (green), Urgent (red)
  - Priority ordering
  - Displays on Barter Feed and Community Board
  - /api/admin/system-messages/* endpoints
- [x] **Filterable Feeds**
  - Barter Feed: Nearby, Network, Verified, Category (Goods/Services/Skills)
  - Community Board: Nearby, Network, Verified, Topic filter
  - Clear filters button
  - Filter pill UI with active state styling
- [x] **Bug Fix**: Added validation for empty/whitespace title and description in barter post creation
- [x] **Push Notifications for Community Board** - Already implemented:
  - Notification when someone likes your community post
  - Notification when someone comments on your community post
  - Notification when someone replies to your comment
  - All UI flows verified working

## What Was Completed (April 2, 2026)
- [x] **Enhanced PWA Features** - Full Progressive Web App implementation
  - PWA manifest.json with app metadata, icons, and splash screen config
  - Enhanced Service Worker with static asset caching and offline fallback
  - Custom offline.html page with brand styling and retry button
  - App icons generated at 8 sizes (72, 96, 128, 144, 152, 192, 384, 512)
  - "Install App" button in sidebar (visible on iOS or when browser supports beforeinstallprompt)
  - iOS-specific install instructions modal with step-by-step guide
  - PWAContext for managing install state across the app
  - Updated index.html with Apple PWA meta tags, theme color, and manifest link
  - Service Worker registration on page load
- [x] Terms of Service / Community Guidelines acceptance on registration
  - Checkbox must be accepted before joining
  - Modal with full guidelines (user responsible for following laws, no harassment, no violence, liability disclaimer)
  - "I Accept" button auto-checks the agreement
- [x] Theme toggle UI regression fix
  - Updated MessagesPanel.js to use CSS variables instead of hardcoded colors
  - Updated TradeNetworkPanel.js to use CSS variables instead of hardcoded colors
  - Added theme-aware utility classes to App.css
  - Verified light and dark mode work correctly across all components
- [x] Verified cookie fix for browser preview authentication
  - Confirmed users and posts display correctly after login
- [x] **Expandable Profile Sections** - User profiles now have expandable sections when viewing others
  - Skills, goods, and services sections show "+X more" when items exceed initial limit
  - Bio text is truncatable with "Read more" link for long descriptions
  - Clicking on items with details shows tooltip with quantity and description
- [x] **Detailed Items Feature** - Goods, skills, and services can now include description and quantity
  - Items stored as {name, description, quantity} objects (all fields optional except name)
  - Backward compatible with old string-format items
  - Profile editing: pencil icon to add/edit quantity and description per item
  - Post creation: edit button on each item to add details
  - Feed display: quantities shown in parentheses on badges
  - Profile view: click items to see full details in tooltip

## Test Credentials
- Production Admin: deathproofrebel@protonmail.com / (set via PROD_ADMIN_PASSWORD env var)
- Preview Admin: williamrhodes764@protonmail.com / Peaches1776@ (role: admin)
- Demo User: demo@rebeltrade.net / demo123 (role: user)

## Code Quality Improvements (April 2, 2026)
- [x] **Security**: Moved hardcoded credentials in test files to environment variables
- [x] **React Hooks**: Fixed missing dependencies in useEffect hooks (Dashboard, AdminDashboard, CategorySelector, ProfilePanel, UserProfileView, Register)
- [x] **React Keys**: Fixed array index as key anti-patterns in TradeDealsPanel
- [x] **Production Seed**: seed_production.py now requires PROD_ADMIN_PASSWORD env variable
- [x] **Deployment**: Fixed .gitignore blocking .env files, fixed CORS configuration
- [x] **WebSocket**: Added /api/ws/ route and fixed connection timing race condition

## Known Issues (Fixed April 2, 2026)
- Messages and Posts APIs are fully functional
- WebSocket connection has a 100ms delay to ensure token availability after login

## Design System
- **Primary Color**: #B45309 (Orange)
- **Recommended/Match**: #F59E0B (Yellow/Amber)
- **Background**: #0C0A09 (Near black)
- **Surface**: #1C1917 (Dark gray)
- **Text Primary**: #E7E5E4
- **Text Secondary**: #A8A29E
- **Accent Green**: #4D7C0F (for "offering" badges)
- **Border Accent**: 2-3px solid #B45309 on key elements
