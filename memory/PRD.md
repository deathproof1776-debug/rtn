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
- **Frontend**: React + Tailwind + Phosphor Icons + Service Worker
- **Auth**: JWT with httpOnly cookies
- **Encryption**: Fernet symmetric encryption for sensitive data
- **Storage**: Local file uploads
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
- [x] **Search Input Padding Fix** (April 2, 2026) - Fixed text bleeding into magnifying glass icon on CategorySelector search inputs
- [x] **Admin Dashboard** (April 2, 2026):
  - Demo account (demo@rebeltrade.net) promoted to admin role
  - Overview tab: Platform stats (users, verified, posts, messages, connections, invites)
  - Users tab: Full user management (search, verify/unverify, promote/demote role, delete)
  - Posts tab: Post moderation (view all, delete posts)
  - Confirmation dialog for destructive actions
  - Admin-only nav item in sidebar (hidden from regular users)
  - Backend endpoints: stats, posts list, role management, user/post deletion

## API Endpoints

### Admin
- POST /api/admin/verify-trader (requires admin role)
- GET /api/admin/users (requires admin role)
- GET /api/admin/stats (requires admin role)
- GET /api/admin/posts (requires admin role)
- DELETE /api/admin/posts/{post_id} (requires admin role)
- PUT /api/admin/users/{user_id}/role (requires admin role)
- DELETE /api/admin/users/{user_id} (requires admin role)

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
- Trade Deals Feature - Formal trade offers/proposals system

### P2 (Medium Priority)
- Video upload support
- User blocking/reporting

### P3 (Enhancement)
- Reply threading for comments
- Location radius settings (specify travel/trade distance)
- Theme toggle UI regression testing (audit hardcoded Tailwind vs CSS variables)

## Test Credentials
- Admin/Demo: demo@rebeltrade.net / demo123 (role: admin)
- System Admin: admin@homesteadhub.com / admin123 (role: admin)
- Seeded users: [name]@example.com / homestead123

## Design System
- **Primary Color**: #B45309 (Orange)
- **Recommended/Match**: #F59E0B (Yellow/Amber)
- **Background**: #0C0A09 (Near black)
- **Surface**: #1C1917 (Dark gray)
- **Text Primary**: #E7E5E4
- **Text Secondary**: #A8A29E
- **Accent Green**: #4D7C0F (for "offering" badges)
- **Border Accent**: 2-3px solid #B45309 on key elements
