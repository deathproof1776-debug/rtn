# Rebel Trade Network - Bartering Platform

## Latest Updates (Jul 10, 2026) — P0: Avatar Deletion, Avatars App-Wide, Clickable Links

### Profile Picture Deletion (DONE, tested 100%)
- Added `handleRemoveAvatar()` in `ProfilePanel.js` — calls `PUT /api/profile` with `avatar: ''`, updates local state + AuthContext
- Trash icon button renders conditionally on avatar (only visible when avatar is set, positioned top-right of avatar)
- `handleSave` now also syncs `avatar` to AuthContext (so Sidebar updates immediately after photo upload)

### Profile Pictures Shown App-Wide (DONE, tested 100%)
- **Sidebar.js**: Bottom user card now shows `user.avatar` image if set, falls back to letter initial
- **MessagesPanel.js**: Conversation list + chat header both now show `conv.user_avatar` / `selectedConversation.user_avatar` with letter fallback
- **ThreadedComments.js**: Comment avatar circles now render `comment.user_avatar` with letter fallback (backend already stores `user_avatar` on comments)
- Already correct: PostCard, CommunityPostCard, ConnectionCard, RecommendedTraderCard, TraderSearchResultCard

### Clickable Links (DONE, tested 100%)
- Created `/app/frontend/src/lib/linkify.js` — `linkifyText(text)` splits on URL regex, returns array with `<a>` elements for http/https URLs
- Applied to: PostCard.js (description), CommunityPostCard.js (content), MessagesPanel.js (message bubbles), ThreadedComments.js (comment content)


- **Root-cause context**: user reported "Something went wrong. Please try again." on the installed PRODUCTION PWA. That message is the login fallback shown ONLY when there is no structured error response (network/CORS/server-unreachable), NOT for wrong credentials (which returns 401 `Invalid email or password`).
- **CORS hardening** (`server.py`): when `CORS_ORIGINS="*"`, now uses `allow_origin_regex=".*"` with `allow_credentials=True` (spec-valid for credentialed cookie auth; a literal `*` is rejected by browsers on credentialed requests). Note: the Emergent ingress also injects CORS headers; preview is same-origin so CORS isn't enforced there.
- **PWA service worker** (`public/sw.js`): bumped `CACHE_NAME` v2→v3 so a redeploy purges stale cached assets on activate (prevents installed PWAs being trapped on old bundles).
- **Login error UX** (`Login.js`): `handleSubmit`/`handle2FA` now branch on `err.response` — real API errors show the server detail; a missing response shows "Couldn't reach the server. It may still be starting up after a deployment — please wait a moment and try again." (clarifies connectivity vs credential failures).
- **seed_production.py**: removed `ENCRYPTION_KEY` default fallback (matches `database.py` fail-loud behavior).
- Verified on preview (iteration_29.json, 100%): all 3 accounts log in, wrong password → specific error, session persists on refresh. Production bug NOT reproducible in preview (same-origin); requires redeploy + production env/DB check.

## Latest Updates (Jul 3, 2026) — Escalated reports admin-only + richer explainers + all-user reset

## Latest Updates (Jul 3, 2026) — Onboarding Tour + Achievement Celebrations (P1 engagement)
- **New-user onboarding tour** (`OnboardingTour.js`): one-time 4-step feature explainer (Welcome → Barter Feed/Matches → Trade Network/Deals → Community/Messages/Safety), shown once and gated by `users.has_seen_onboarding`. `POST /api/onboarding/complete` marks it seen. Skippable.
- **Achievement celebration + explainer** (`AchievementCelebration.js`): one-time modal + push notification when a user earns a badge/role. Keys: `verified`, `trusted_trader`, `moderator`. Each modal explains what the badge/role unlocks (perks list).
- **Backend** `achievements.py`: `ACHIEVEMENTS` config + `grant_achievement(user_id, key)` → `$addToSet` into `users.pending_achievements` + fires `send_push_notification`. Granted only on TRUE transitions (won't retro-fire for already-verified/trusted users):
  - `admin.py verify_trader` → grants `verified`
  - `admin.py update_user_role` → grants `moderator`
  - `trades.py check_and_award_trusted_trader` → grants `trusted_trader` (now transition-guarded)
- `routes/engagement.py`: `POST /api/onboarding/complete`, `POST /api/achievements/ack` ({key}). `/api/auth/me` + login payload now return `has_seen_onboarding` + `pending_achievements`.
- Wired into `Dashboard.js`: tour shows first for new users; achievement celebrations queue after (one at a time, acked to clear). Tested E2E (curl + screenshot): tour steps, moderator celebration, ack persistence all pass.
- **Backfill for existing users (Jul 3, 2026)**: `backfill_pending_achievements()` runs lazily on login + `/api/auth/me`. Any existing user who already holds `verified`/`trusted_trader`/`moderator` but never saw its explainer gets it queued on their next session — deduped, and tracked via `users.achievements_seen` (recorded on ack) so it shows exactly once and never repeats. The onboarding tour already reaches existing users since a missing `has_seen_onboarding` is treated as unseen. Verified via curl: login/`/me` backfills, ack records `achievements_seen`, no re-adds after ack.

## Latest Updates (Jul 3, 2026) — Moderator Role Tier (P1) + P0 Security Hardening

### P0 Security Hardening (DONE, tested)
- **Per-user write rate-limits** via slowapi `user_rate_limit_key` (keyed by JWT `sub`, falls back to IP): posts 20/min, likes 60/min, comments 30/min, community 10/min, gallery upload 10/min, messages 60/min, report 10/hr, network request 20/hr. Verified 429 fires after limit.
- **Removed `ENCRYPTION_KEY` fallback** in `database.py` → now `os.environ["ENCRYPTION_KEY"]` (fails loud). Key present in `.env`.
- **Auth cookies audit**: HttpOnly ✅ + Secure ✅ confirmed. SameSite kept at `None` (REQUIRED for cross-origin preview/prod; Strict would break login — user approved).

### Moderator Role Tier (Hybrid, DONE, tested)
- New `moderator` role. `auth.py`: `is_staff()` helper + `require_moderator` dependency (moderator OR admin).
- **Hybrid assignment**: admin promotes users via `PUT /api/admin/users/{id}/role` (now accepts `moderator`). Eligibility rule: only `is_verified` users can be promoted to moderator (400 otherwise).
- **Moderator abilities**: view/resolve/dismiss reports, **escalate to admin** (`PUT /api/admin/reports/{id}/escalate`), delete flagged posts/comments/community posts/gallery items (via `is_staff` checks in delete routes + `isAdmin` prop extended to moderators in Feed/CommunityBoard).
- **Moderator CANNOT**: verify users, change roles, send system announcements, block/ban (all admin-only, enforced via `require_admin`).
- Report docs gained `escalated`, `escalated_by`, `escalated_by_name`, `escalated_at`, `resolved_by_name`. Report list supports `status=escalated` filter; stats include `escalated` count.
- Moderator actions logged to `audit_log`.
- **Frontend**: `ModerationDashboard.js` page (moderator-only, reuses `ReportsPanel`); Sidebar shows "Moderation" for moderators, "Admin Dashboard" for admins. `QuickUserRow` gets "Make/Remove Moderator" action (disabled unless verified) + moderator badge. `ReportsPanel` gets Escalate button + Escalated badge + Escalated filter tab. `StatsBar` gains Trusted + Moderators cards.
- Test accounts: mod@homesteadhub.com / Modpass123!, verified@homesteadhub.com / Verified123! (see test_credentials.md).

## Latest Updates (Feb 10, 2026) — User Blocking & Reporting (P1 Task 2)
- **Feature**: Mutual user blocking — if A blocks B, neither sees the other's posts, comments, community posts, messages, or network suggestions. `POST/DELETE /api/moderation/block/{user_id}`, `GET /api/moderation/blocks`, `GET /api/moderation/blocks/check/{user_id}`.
- **Feature**: Content reporting with admin queue — `POST /api/moderation/report` (target_type: user/post/comment/community_post/gallery_item; 8 reasons: spam, harassment, hate_speech, nsfw, scam, impersonation, violence, other). Duplicate pending reports deduped.
- **Admin**: `GET /api/admin/reports?status=`, `PUT /api/admin/reports/{id}` (resolve/dismiss/reopen with note), `GET /api/admin/reports/stats`.
- **New collections**: `blocks` (unique idx blocker_id+blocked_id), `reports` (compound idx on status+created_at, and reporter+target dedup idx).
- **Frontend**:
  - `ReportModal.js` + `BlockedUsersPanel.js` in `components/moderation/`
  - Admin `ReportsPanel.js` (filter tabs pending/resolved/dismissed/all with counts, resolve/dismiss actions)
  - `PostMenu` now shows Report Post + Block User for other users' posts
  - `UserProfileView` has Report + Block buttons
  - `SecuritySettings` gets Blocked Users section
  - `Feed` listens to `rtn:user-blocked` DOM event → drops blocked user's posts without refresh
- **Filtering wired into**: `/api/posts`, `/api/posts/matches`, `/api/posts/{id}/comments`, `/api/community`, `/api/conversations`, `/api/messages` (403 on blocked), `/api/network/request` (403), `/api/network/recommended`.
- **Tests**: `/app/backend/tests/test_moderation_block_report.py` — 9/9 pytest pass. E2E frontend flows 100% pass (`iteration_27.json`).

## Latest Updates (Feb 10, 2026) — Frontend Component Refactoring (P1 Task 1)
- **Refactor**: Split large frontend components for maintainability with zero regressions (tested via `iteration_26.json`, 100% frontend pass)
  - `AdminDashboard.js`: 557 → 192 lines (−66%). Extracted into `components/admin/`: `StatsBar`, `StatCard`, `AnnouncementsSection`, `AnnouncementModal`, `UsersPanel`, `QuickUserRow`, `PostsPanel`, `CommunityPanel`, `CommunityPostRow`, `ActivityLogPanel`, `ConfirmDialog`.
  - `PostCard.js`: 451 → 329 lines (−27%). Extracted `components/post/PostMedia`, `PostActions`, `PostMenu`.
  - `Gallery.js`: 548 → 176 lines (−68%). Extracted `components/gallery/GalleryGrid`, `GalleryItemModal`, `UploadModal`.
- **Cleanup**: Removed unused `onToggle` prop on AnnouncementModal and dead `handleDelete` function in Gallery.js.

## Latest Updates (May 6, 2026)
- **Bug Fix**: Notifications toggle didn't subscribe — fixed in `NotificationContext.js` and `NotificationBell.js`. Now uses `navigator.serviceWorker.ready` to wait for SW activation, listens to permission-change events, keeps dropdown open after toggle so users see status, and reuses any existing push subscription.
- **Backlog added**: NSFW image/video moderation (P2) — recommended `opennsfw2` server-side classifier on gallery + post images + avatars; auto-reject score > 0.85, blur + reveal toggle on 0.5–0.85; admin override.

## Latest Updates (May 2, 2026) — Security Hardening (P1 High Impact)
- **Feature**: Rate limiting on `/api/auth/login` (10/min) and `/api/auth/register` (5/hr) via slowapi
- **Feature**: Account lockout — 5 failed logins per email triggers 15-minute lockout (HTTP 429)
- **Feature**: TOTP-based 2FA (pyotp + QR) with 8 one-time recovery codes; new login flow returns `{two_factor_required, challenge_token}` then completes via `/api/auth/login/2fa`
- **Feature**: Password strength validation via zxcvbn; minimum 8 chars + score ≥2; live meter on Register and password change
- **Feature**: Refresh-token rotation with server-side storage — users can list active sessions, sign out individual sessions, or "Sign out everywhere"
- **Feature**: Self-service Password Change (revokes all other sessions on success)
- **New routes**: `/api/security/2fa/{setup,confirm,disable,recovery-codes/regenerate}`, `/api/security/sessions`, `/api/security/sessions/{revoke,revoke-others}`, `/api/security/password/change`, `/api/auth/password/check`
- **New components**: `SecuritySettings.js`, `PasswordStrengthMeter.js`; `Sidebar` gets new "Security" tab
- **DB**: New collections `login_attempts`, `refresh_tokens`, `recovery_codes` with indexes

## Previous Updates (April 28, 2026)
- **Feature**: Trusted Trader Badge (green) - Auto-awarded after 5 mutually confirmed completed trades
- **Feature**: Trade Completion Confirmation - Both parties must confirm trade completion
- **Feature**: Invite restricted to verified traders only
- **Feature**: Admin Dashboard consolidated - All functions on single page with Announcements at top
- **Feature**: Community Feed added to Admin Dashboard
- **Update**: PWA app icon updated to orange shield with "RTN" letters

## Previous Updates (April 4, 2026)
- **Feature**: Edit Post - users can now edit their own barter posts (title, description, category, offering, looking_for)
- **Feature**: Edit Comment - users can edit their own comments with inline editor, shows "(edited)" indicator
- **Feature**: CreatePostModal now uses CategorySelector dropdowns for Offering/Looking For (same as profile)
- **Bug Fix**: PostCard.js now displays user avatars when available (previously only showed initials)
- **Bug Fix**: UserProfileView.js gallery endpoint corrected from `/api/gallery/{userId}` to `/api/gallery/user/{user_id}`

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

### 🔥 P0 — NEXT FORK STARTS HERE (Security Hardening Pass)
1. **Broad write rate-limits** — Extend `slowapi` from just `/auth` to all write endpoints. Apply per-user (not just per-IP):
   - `POST /api/posts` (20/min)
   - `POST /api/posts/{id}/like` (60/min)
   - `POST /api/posts/{id}/comments` (30/min)
   - `POST /api/community` (10/min)
   - `POST /api/gallery/upload` (10/min)
   - `POST /api/messages` (60/min)
   - `POST /api/moderation/report` (10/hour — prevent mod-queue flooding)
   - `POST /api/network/request` (20/hour)
2. **Remove `ENCRYPTION_KEY` fallback** in `backend/database.py:18` — currently defaults to `"default-encryption-key-32b!"` if env var missing. Change to `os.environ["ENCRYPTION_KEY"]` so missing config fails loudly instead of silently encrypting user data with a publicly-known key.
3. **Verify auth cookies flags** — Ensure `/api/auth/login` sets `HttpOnly`, `Secure`, and `SameSite=Strict` on the access/refresh cookies. Audit current implementation.

### 🔴 P1 — Critical App Deficiencies (from review)
- **Frontend test coverage** — Zero `*.test.js` files exist. Add React Testing Library + Vitest/Jest suites for `Feed`, `PostCard`, `PostMenu`, `ReportModal`, `Login`, `Register`. ~2 hours.
- **Admin push/email alerts on new reports** — Currently reports sit silently in the queue until an admin logs in. Wire web-push to all admins on new report + a daily email digest of pending reports.
- **Moderator role tier** — Add a 3rd role (`moderator`) between `user` and `admin`. Can view/resolve reports and delete flagged content, but cannot verify users, change roles, or send system announcements.
- **Unified `ConfirmDialog` replacing `window.confirm()`** — Currently used in `PostCard.handleBlockUser`, `PostMenu` delete, `Gallery.handleDelete`, `BlockedUsersPanel` unblock (native `confirm` is inconsistent with the styled dialog in AdminDashboard). Single reusable component.
- **Sentry / error tracking** — 87 `console.error` calls in frontend + 46 backend `print()` statements go nowhere in production. Add error tracking to see real user issues.

### 🟠 P1 — Trust System Gaps (from review)
- **Trusted Trader downgrade path** — Once earned, `is_trusted_trader` is permanent. Recalculate on trade dispute or admin action. Add `POST /api/admin/revoke-trusted` for manual admin action + auto-recalc job.
- **Trade completion proof requirement** — Currently self-reported; both parties can collude to farm badges. Consider optional photo/receipt upload on trade completion, or geotagged meetup check-in.
- **Documented verification criteria** — No documented criteria for `is_verified`. Add an admin-facing checklist (identity confirmed, community reference, no active reports, X days on platform) and store which criteria were met on verify action.
- **Boost verified/trusted users in feed algorithm** — Currently only `is_network` (+200) and `is_nearby` (+100) affect `feed_score`. Add +50 for verified, +30 for trusted trader.
- **"Trusted Trader unlocked!" push notification** — 5th completed trade auto-awards silently. Trigger a push to celebrate the milestone (engagement + retention).
- **Admin stats: `trusted_users` count card** — Only `verified_users` is shown. Add matching card for consistency.
- **Cold-start invite chicken-and-egg** — Unverified users can't send invites. Options: (a) allow 1 invite per new user regardless of verification, (b) auto-verify after N days + N posts, or (c) admin bulk-verify seed cohort.
- **"Community Guardian" badge for good-faith reporters** — Award users whose reports get resolved (not dismissed) 3+ times. Incentivizes moderation participation.

### 🟡 P2 — Scale & Consistency (from review)
- **Feed denormalization** — Store `is_verified`, `is_trusted_trader`, and `location_hash` on each post at write time. Removes N+1 user lookup in `/api/posts`.
- **Standardize soft-delete** — Community posts use `is_deleted: true`; barter posts hard-delete. Unify to soft-delete on both with 30-day admin-recoverable window + audit log.
- **Object storage lifecycle cleanup** — When a post/gallery item is deleted, orphaned files stay in Emergent Object Storage. Add a background cleanup job on delete + a weekly orphan sweep.
- **Per-user announcement dismissal persistence** — Dismissed system banners reappear on refresh. Persist per-user in DB.
- **Account deletion + data export** — GDPR/CCPA. Currently no way to delete an account or download personal data. Values-inconsistent for an "exit the matrix" brand.
- **Location radius settings** — Allow users to specify travel/trade distance (5mi, 25mi, 100mi, unlimited). Expand matching beyond exact city string comparison.

### 🟢 P3 — Enhancements
- **Trade ratings/reviews** — After a completed trade, both parties can leave 1–5 stars + optional comment. Aggregate onto user profile.
- **AI NSFW image moderation** (`opennsfw2`) — Server-side classifier on gallery uploads + post images + avatars. Auto-reject > 0.85, blur + reveal on 0.5–0.85, admin override.
- **Threaded reply notifications** — Currently notify the parent commenter; extend to notify the whole thread on a "watched" flag.
- **Moderator activity leaderboard** — Show admin/mod who resolved most reports this month (accountability + gamification).

### 🔵 Frontend Refactoring Backlog (from review)
- `UserProfileView.js` (488 lines) — Extract `ProfileHeader`, `ProfileActions`, `ProfileSkills`, `ExpandableBio` into `components/profile/`.
- `CategorySelector.js` (427 lines) — Split search + list + selected chips.
- `FeedFilters.js` (410 lines) — Extract filter groups into sub-components.
- `ProfilePanel.js` (386 lines) — Slim down; extract goods/services editor.

## What Was Completed (April 3, 2026)
- [x] **Security Audit** - Comprehensive security review completed
  - All routes verified for authentication requirements
  - Admin routes properly protected with role checks
  - File upload validation enforced (type whitelist, size limits)
  - No hardcoded secrets, injection vulnerabilities, or _id leaks
  - WebSocket JWT validation verified
  - CORS properly configured
  - Full audit report: /app/memory/SECURITY_AUDIT.md
- [x] **Bug Fix: Video Upload on Community Board** - Community Board now supports video uploads
  - Updated CreateCommunityPostModal to accept both image/* and video/* file types
  - Updated CommunityPostCard to detect and render videos with <video> element and controls
  - Videos detected by extension (.mp4, .mov, .webm, .mpeg) or is_video flag
- [x] **Bug Fix: Gallery Failing to Load** - Fixed gallery routing conflict
  - Added new endpoint GET /api/gallery/user/{user_id} for fetching user galleries
  - Returns {items: [], user_name: ""} structure with is_liked flag for each item
  - Fixed frontend Gallery.js to call correct endpoint
- [x] **Post Delete Feature** - Users can delete their own posts, admins can delete any post
  - Added DELETE /api/posts/{post_id} endpoint with authorization checks
  - PostCard.js shows "Delete Post" option in dropdown menu for own posts or admins
  - Feed.js handles post deletion with instant UI removal
  - Security: Regular users get 403 when trying to delete others' posts
- [x] **Admin View Profile** - Admin can view user profiles from Admin Dashboard
  - Added "View Profile" option to user action dropdown in Users tab
  - Navigates to user's profile via existing onViewProfile handler
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
