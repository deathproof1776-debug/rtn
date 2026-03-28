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

## Architecture
- **Backend**: FastAPI + MongoDB + WebSocket + pywebpush
- **Frontend**: React + Tailwind + Phosphor Icons + Service Worker
- **Auth**: JWT with httpOnly cookies
- **Encryption**: Fernet symmetric encryption for sensitive data
- **Storage**: Local file uploads
- **Push Notifications**: Web Push API with VAPID keys

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
- [x] **Comments on posts** (March 2026) - Full CRUD with encryption, toggle expand/collapse, delete authorization
- [x] **Location-based matching** (March 2026) - Text-based location matching, Nearby badges, location prioritization in matches, Nearby Homesteaders panel, filter by nearby
- [x] **Push Notifications** (March 2026) - Browser push notifications for messages, comments, likes. Service Worker, VAPID auth, subscription management UI
- [x] **Mobile UI Optimization** (March 2026) - Mobile-first responsive design with bottom navigation, mobile header, slide-out sidebar drawer, optimized feed and profile layouts
- [x] **Pull-to-Refresh** (March 2026) - Native-feeling pull-down refresh on mobile feed
- [x] **Profile Loading Bug Fix** (March 2026) - Fixed /api/auth/me returning `_id` instead of `id`
- [x] **Rebranding to "Rebel Trade Network"** (March 28, 2026) - Changed app name from HomesteadHub, updated all branding locations
- [x] **Orange Borders/Trim** (March 28, 2026) - Added orange accent borders to sidebar, right panel, mobile header, mobile nav, post cards
- [x] **Verified Trader Badge System** (March 28, 2026) - Admin can verify traders, verified badge displays on posts and profiles

## Mobile UI Components
- **MobileHeader.js** - Hamburger menu, branding, notification bell, create post button
- **MobileNav.js** - Bottom navigation with Feed, Post (prominent), Messages, Profile
- **Sidebar drawer** - Slide-out drawer for mobile navigation with overlay
- **Responsive CSS** - Mobile-first approach with breakpoints at 768px (tablet) and 1024px (desktop)
- **Pull-to-Refresh** - Native-feeling pull-to-refresh on mobile feed with visual indicator

## Verified Trader Badge System
- Admin users can verify/unverify traders via POST /api/admin/verify-trader
- Verified badge displays on posts in feed (orange gradient badge with checkmark)
- Verified badge displays on profile panel for verified users
- Login and auth endpoints return `is_verified` and `role` fields
- Admin can view all users via GET /api/admin/users

## Prioritized Backlog
### P0 (Critical)
- None remaining for MVP

### P1 (High Priority)
- None

### P2 (Medium Priority)
- Video upload support
- User blocking/reporting
- Advanced search filters

### P3 (Enhancement)
- Reply threading for comments
- Location radius settings (specify travel/trade distance)

## Test Credentials
- Admin: admin@homesteadhub.com / admin123 (role: admin, is_verified: true)

## API Endpoints
### Auth
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/refresh

### Admin
- POST /api/admin/verify-trader (requires admin role)
- GET /api/admin/users (requires admin role)

### Profile
- PUT /api/profile
- GET /api/profile/{user_id}

### Posts
- POST /api/posts
- GET /api/posts (supports ?nearby_only=true filter)
- GET /api/posts/matches (location-prioritized with match_score)
- POST /api/posts/{id}/like (triggers push notification)

### Comments
- POST /api/posts/{post_id}/comments - Create comment (encrypted, triggers push notification)
- GET /api/posts/{post_id}/comments - Get all comments (decrypted)
- DELETE /api/posts/{post_id}/comments/{comment_id} - Delete comment (owner or post owner)

### Messages
- GET /api/conversations
- POST /api/messages (triggers push notification)
- GET /api/messages/{user_id}

### Users
- GET /api/users/nearby - Get users in same location
- GET /api/users/search

### Push Notifications
- GET /api/notifications/vapid-public-key - Get VAPID public key (no auth)
- POST /api/notifications/subscribe - Subscribe to push notifications
- POST /api/notifications/unsubscribe - Unsubscribe from push notifications
- GET /api/notifications/status - Get subscription status
- POST /api/notifications/test - Send test notification

### Other
- POST /api/upload
- WebSocket: /ws/{user_id}

## Data Models
### Users (with verification)
```json
{
  "_id": "ObjectId",
  "email": "string",
  "name": "string",
  "location": "encrypted string",
  "bio": "encrypted string",
  "skills": ["array"],
  "goods_offering": ["array"],
  "goods_wanted": ["array"],
  "services_offering": ["array"],
  "services_wanted": ["array"],
  "avatar": "string (URL)",
  "role": "user | admin",
  "is_verified": "boolean",
  "verified_at": "ISO timestamp (if verified)",
  "created_at": "ISO timestamp"
}
```

### Posts (with verification status)
```json
{
  "_id": "ObjectId string",
  "user_id": "string",
  "user_name": "string",
  "user_location": "string (decrypted)",
  "is_nearby": "boolean",
  "is_verified": "boolean",
  "match_score": "number (for /api/posts/matches)",
  "title": "string",
  "description": "encrypted string",
  "category": "string",
  "offering": ["array"],
  "looking_for": ["array"],
  "created_at": "ISO timestamp"
}
```

### Push Subscriptions
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "endpoint": "string (push service URL)",
  "keys": {
    "p256dh": "string",
    "auth": "string"
  },
  "created_at": "ISO timestamp"
}
```

## Design System
- **Primary Color**: #B45309 (Orange)
- **Background**: #0C0A09 (Near black)
- **Surface**: #1C1917 (Dark gray)
- **Text Primary**: #E7E5E4
- **Text Secondary**: #A8A29E
- **Accent Green**: #4D7C0F (for "offering" badges)
- **Border Accent**: 2-3px solid #B45309 on key elements
- **Verified Badge**: Gradient from #B45309 to #92400E with glow effect
