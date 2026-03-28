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
- [x] Comments on posts - Full CRUD with encryption
- [x] Location-based matching - Nearby badges, location prioritization
- [x] Push Notifications - Browser push for messages, comments, likes
- [x] Mobile UI Optimization - Bottom nav, mobile header, slide-out sidebar
- [x] Pull-to-Refresh - Native-feeling pull-down refresh on mobile feed
- [x] Rebranding to "Rebel Trade Network" - Updated all branding
- [x] Orange Borders/Trim - Added orange accent borders throughout
- [x] Verified Trader Badge System - Admin verification with badges
- [x] **Trade Network Feature** (March 28, 2026) - LinkedIn-style mutual connections:
  - Send/receive network requests
  - Accept/decline incoming requests
  - View connected traders
  - Remove connections
  - Network members get +200 priority in feed algorithm
  - "My Trade Network" section in sidebar + profile panel
  - User profile modal with "Add to Trade Network" button
  - Network badge counts in navigation
  - Push notifications for network requests

## Trade Network Feature Details
### Backend Endpoints
- `POST /api/network/request` - Send network request
- `POST /api/network/respond` - Accept/decline request
- `GET /api/network/requests/pending` - Get incoming/outgoing requests
- `GET /api/network/connections` - Get all connections
- `DELETE /api/network/connections/{user_id}` - Remove connection
- `GET /api/network/status/{user_id}` - Check status with user
- `POST /api/network/cancel/{request_id}` - Cancel pending request

### Feed Algorithm Priority
- Network members: +200 score
- Nearby users: +100 score
- Goods/services match: +10 per match

### MongoDB Collections
- `network_connections` - Stores established connections
- `network_requests` - Stores pending/responded requests

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

### Trade Network
- POST /api/network/request
- POST /api/network/respond
- GET /api/network/requests/pending
- GET /api/network/connections
- DELETE /api/network/connections/{user_id}
- GET /api/network/status/{user_id}
- POST /api/network/cancel/{request_id}

### Profile
- PUT /api/profile
- GET /api/profile/{user_id}

### Posts
- POST /api/posts
- GET /api/posts (returns is_network, feed_score for priority)
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

## Data Models
### Network Connections
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "connected_user_id": "string",
  "created_at": "ISO timestamp"
}
```

### Network Requests
```json
{
  "_id": "ObjectId",
  "from_user_id": "string",
  "from_user_name": "string",
  "from_user_avatar": "string",
  "to_user_id": "string",
  "status": "pending | accepted | declined",
  "created_at": "ISO timestamp",
  "responded_at": "ISO timestamp (optional)"
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
- **Network Badge**: Orange background with handshake icon
