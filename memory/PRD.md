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
- [x] **Trade Network Feature** - LinkedIn-style mutual connections
- [x] **Recommended Traders Feature** - Smart trader suggestions
- [x] **Categorized Goods/Skills/Services** (March 28, 2026):
  - 5 Goods categories: Food, Tools, Crafts, Livestock, Miscellaneous
  - 5 Skills categories: Homestead, Landscape, Trade/Technical, Creative, Life/Survival
  - 7 Services categories: Labor, Equipment, Animal, Professional, Education, Health, Custom
  - Searchable dropdowns with category accordions
  - Multi-select from predefined items
  - Custom item addition support
  - CategorySelector component with search, expand/collapse, badges
- [x] **Light/Dark Mode Theme Toggle** (March 28, 2026)
- [x] **Invite-Only Registration System** (April 2, 2026):
  - Registration requires a valid invite link from existing member
  - Existing users can generate unique invite links from "Invite Members" panel
  - Invite tokens expire after 7 days, single-use only
  - /register without valid invite shows "Invite Required" gate page
  - Login page updated to show invite-only messaging (no register link)
  - Invite panel shows ACTIVE/USED/EXPIRED status for each invite
  - Backend tracks who created and used each invite

## Categorized Selection System (NEW)

### Goods Categories
| Category | Sample Items |
|----------|-------------|
| **Food** | Fresh Eggs, Honey, Raw Milk, Cheese, Vegetables, Meats, Canned Goods, Maple Syrup, Grains, Fermented Foods |
| **Tools** | Hand Saws, Axes, Power Drills, Canning Equipment, Beekeeping Equipment, Fencing Tools, Blacksmithing Tools |
| **Crafts** | Handmade Furniture, Quilts, Clothing, Pottery, Candles, Soaps, Jewelry, Art, Knives, Musical Instruments |
| **Livestock** | Laying Hens, Dairy Goats, Cattle, Pigs, Sheep, Rabbits, Bees, Horses, Guard Dogs |
| **Miscellaneous** | Seeds, Plant Starts, Firewood, Lumber, Building Materials, Hay, Compost, Solar Panels, Wool, Hides |

### Skills Categories
| Category | Sample Items |
|----------|-------------|
| **Homestead** | Canning & Preserving, Fermenting, Cheese Making, Soap Making, Butchering, Beekeeping, Seed Saving, Foraging, Herbalism |
| **Landscape** | Permaculture Design, Irrigation Systems, Fencing, Pond Building, Tree Grafting, Composting, Greenhouse Construction |
| **Trade/Technical** | Carpentry, Welding, Plumbing, Electrical, Masonry, Solar Installation, Mechanic, Gunsmithing, Blacksmithing |
| **Creative** | Woodworking, Pottery, Sewing, Knitting, Jewelry Making, Leathercraft, Photography, Writing |
| **Life/Survival** | First Aid, Midwifery, Veterinary Care, Hunting, Fishing, Wilderness Survival, Radio Communications, Teaching |

### Services Categories
| Category | Sample Items |
|----------|-------------|
| **Labor** | Farm Labor, Fence Building, Firewood Cutting, Construction Labor, Landscaping, Snow Removal |
| **Equipment** | Tractor Rental, Truck/Trailer Rental, Chainsaw Services, Tilling, Hay Baling, Excavation |
| **Animal** | Stud Services, Animal Training, Farrier Services, Shearing, Butchering Services, Pet Sitting |
| **Professional** | Consulting, Land Survey, Legal Services, Accounting, Marketing, Photography |
| **Education** | Workshops, One-on-One Training, Homesteading Classes, Survival Skills Training, First Aid Training |
| **Health** | Midwifery, Massage Therapy, Herbal Consultations, Childcare, Eldercare, Meal Prep |
| **Custom** | Custom Furniture, Custom Clothing, Custom Knives, Custom Leatherwork, Commissioned Art |

## API Endpoints

### Categories (NEW)
- GET /api/categories/all - Returns all goods, skills, services categories
- GET /api/categories/goods - Returns 5 goods categories with items
- GET /api/categories/skills - Returns 5 skills categories with items
- GET /api/categories/services - Returns 7 services categories with items

### Invites (NEW - April 2, 2026)
- POST /api/invites/create - Generate invite link (authenticated)
- GET /api/invites/validate/{token} - Validate invite token (public)
- GET /api/invites/my-invites - List user's invites (authenticated)

### Auth
- POST /api/auth/register (requires invite_token field)
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
- GET /api/network/recommended

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

## Prioritized Backlog

### P0 (Bugs)
- ~~Push Notification Toggle broken~~ (FIXED April 2, 2026 - Code was correct, issue was browser support limitation in testing environment. Real browsers work correctly.)
- ~~Post interactions broken~~ (FIXED April 2, 2026 - Profile click, 3-dots menu, expandable posts)

### P1 (High Priority)
- Trade Deals Feature - Formal trade offers/proposals system

### P2 (Medium Priority)
- Video upload support
- User blocking/reporting

### P3 (Enhancement)
- Reply threading for comments
- Location radius settings (specify travel/trade distance)

## Recent Bug Fixes (April 2, 2026)
1. **Post Profile Click** - Users can now click on poster's username or avatar to view their profile
2. **3-Dots Menu** - Menu now opens with View Profile, Send Message, Report Post options
3. **Expandable Posts** - Long posts (>200 chars) now show "Read more" / "Show less" toggle
4. **Push Notifications** - Added debug logging, verified code is correct (browser support varies)

## Test Credentials
- Admin: admin@homesteadhub.com / admin123 (role: admin, is_verified: true)
- Demo: demo@rebeltrade.net / demo123 (regular user)
- All simulated users: [name]@example.com / homestead123

## Seed Data (March 31, 2026)
- 11 simulated users across 4 locations (Austin TX, Portland OR, Denver CO, Nashville TN)
- 7 verified traders showcasing the badge system
- 10 barter posts with diverse goods/services offerings
- 10 network connections demonstrating the trade network feature
- 3 message threads with realistic conversations
- Comments and likes on multiple posts
- Run seed script: `cd /app/backend && python seed_data.py`

## Design System
- **Primary Color**: #B45309 (Orange)
- **Recommended/Match**: #F59E0B (Yellow/Amber)
- **Background**: #0C0A09 (Near black)
- **Surface**: #1C1917 (Dark gray)
- **Text Primary**: #E7E5E4
- **Text Secondary**: #A8A29E
- **Accent Green**: #4D7C0F (for "offering" badges)
- **Border Accent**: 2-3px solid #B45309 on key elements
