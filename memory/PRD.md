# HomesteadHub - Bartering Network Platform

## Original Problem Statement
Social media platform for homesteaders, survivalists, and those exiting corporate control. Features Facebook aesthetics with LinkedIn functionality. Profiles include location, skills, goods/services for barter. Photo/video uploads, direct messaging, main feed with matching algorithm. Full encryption.

## User Choices
- JWT-based custom auth (email/password)
- Local file storage for photos/videos
- Full encryption (messages + all user data)
- WebSocket-based real-time chat
- Rebel homesteader vibe aesthetic

## Architecture
- **Backend**: FastAPI + MongoDB + WebSocket
- **Frontend**: React + Tailwind + Phosphor Icons
- **Auth**: JWT with httpOnly cookies
- **Encryption**: Fernet symmetric encryption for sensitive data
- **Storage**: Local file uploads

## What's Been Implemented (Jan 2026)
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

## Prioritized Backlog
### P0 (Critical)
- None remaining for MVP

### P1 (High Priority)
- Enhanced matching algorithm
- Comment system on posts
- Push notifications

### P2 (Medium Priority)
- Video upload support
- User blocking/reporting
- Advanced search filters
- Location-based matching

## Test Credentials
- Admin: admin@homesteadhub.com / admin123

## API Endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- PUT /api/profile
- GET /api/profile/{user_id}
- POST /api/posts
- GET /api/posts
- POST /api/posts/{id}/like
- GET /api/conversations
- POST /api/messages
- GET /api/messages/{user_id}
- POST /api/upload
- GET /api/users/search
- WebSocket: /ws/{user_id}
