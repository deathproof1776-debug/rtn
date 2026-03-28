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

## Prioritized Backlog
### P0 (Critical)
- None remaining for MVP

### P1 (High Priority)
- Location-based matching
- Push notifications

### P2 (Medium Priority)
- Video upload support
- User blocking/reporting
- Advanced search filters
- Verified Homesteader badge system

## Test Credentials
- Admin: admin@homesteadhub.com / admin123

## API Endpoints
### Auth
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/refresh

### Profile
- PUT /api/profile
- GET /api/profile/{user_id}

### Posts
- POST /api/posts
- GET /api/posts
- GET /api/posts/matches
- POST /api/posts/{id}/like

### Comments
- POST /api/posts/{post_id}/comments - Create comment (encrypted)
- GET /api/posts/{post_id}/comments - Get all comments (decrypted)
- DELETE /api/posts/{post_id}/comments/{comment_id} - Delete comment (owner or post owner)

### Messages
- GET /api/conversations
- POST /api/messages
- GET /api/messages/{user_id}

### Other
- POST /api/upload
- GET /api/users/search
- WebSocket: /ws/{user_id}

## Data Models
### Comments (embedded in posts)
```json
{
  "id": "ObjectId string",
  "user_id": "string",
  "user_name": "string",
  "user_avatar": "string",
  "content": "encrypted string",
  "created_at": "ISO timestamp"
}
```
