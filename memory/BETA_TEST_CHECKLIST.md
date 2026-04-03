# REBEL TRADE NETWORK - BETA TEST ACTION LIST
## New Features & Fixes Since Last Deployment

---

### ACCOUNT & LOGIN
1. Go to app URL and verify login page loads
2. Log in with your credentials
3. Verify you land on the dashboard after login
4. Click profile icon, verify your profile loads
5. Test logout, verify redirect to login page
6. Log back in to continue testing

---

### COMMUNITY BOARD (NEW)
1. Click "Community" in sidebar navigation
2. Verify Community Board page loads with posts
3. Click "New Post" button
4. In modal: Select a Topic from dropdown (Homesteading, Off-Grid, Prepping, etc.)
5. Enter a Title and Content
6. Optionally upload up to 5 images
7. Click Post, verify post appears in feed
8. Like a post, verify like count increases
9. Add a comment to a post
10. Reply to an existing comment (nested thread test)
11. Delete your own comment, verify removal

---

### COMMUNITY BOARD FILTERS (NEW)
1. On Community Board, click "Filters" dropdown
2. Enable "Nearby" filter, verify posts filter to local area
3. Enable "Network" filter, verify posts from connections only
4. Enable "Verified" filter, verify verified badge posts only
5. Enable "Has Media" filter, verify image posts only
6. Select a Topic filter, verify topic-specific posts
7. Select "This Week" from time range, verify recent posts only
8. Select "Most Popular" from sort, verify high-like posts first
9. Click "Clear" to reset all filters

---

### BARTER FEED FILTERS (NEW)
1. Click "Feed" in sidebar navigation
2. Click "Filters" dropdown
3. Test "Nearby", "Network", "Verified" toggles
4. Test "Goods", "Services", "Skills" category filters
5. Test "Today", "This Week", "This Month" time range
6. Test "Most Popular", "Most Commented", "Newest" sort
7. Verify filter combinations work together

---

### SYSTEM ANNOUNCEMENTS (NEW - ADMIN ONLY)
1. If you are an admin: Go to Admin Dashboard
2. Click "System Messages" tab
3. Create new announcement with type (Info, Warning, Success, Urgent)
4. Toggle "Active" status
5. Go to Feed and Community Board, verify banner displays
6. If not admin: Verify you see admin announcements as scrolling banners

---

### TRADE NETWORK
1. Click "Trade Network" in sidebar
2. Check "Recommended" tab, verify trader suggestions load
3. Click "Connect" on a recommended trader
4. Check "Requests" tab, verify request shows in "Sent Requests"
5. Check "Network" tab, verify existing connections display
6. View a connection's profile by clicking their name

---

### TRADE DEALS
1. Click "Trade Deals" in sidebar
2. Check "Incoming" tab for any trade offers
3. Check "Outgoing" tab for trades you've proposed
4. Check "History" tab for completed/declined deals
5. If you have an incoming trade: Accept, Decline, or Counter
6. Propose a new trade from someone's profile or post

---

### GALLERY
1. Go to your profile
2. Click "Gallery" section
3. Upload a photo or video
4. Add a caption
5. Verify upload appears in gallery grid
6. Click on a gallery item to view full size
7. Like the item
8. Add a comment
9. Reply to a comment (nested thread test)

---

### LIGHT/DARK MODE
1. Click the sun/moon icon in the top right corner
2. Verify theme switches from dark to light
3. Verify all text remains readable
4. Verify all panels and cards update colors
5. Navigate to different pages, verify consistency
6. Switch back to original theme

---

### MOBILE RESPONSIVE
1. Open app on mobile device or resize browser to mobile width
2. Verify bottom navigation bar appears (Feed, Network, Post, Messages, Profile)
3. Tap hamburger menu icon, verify sidebar slides out
4. Navigate between sections using bottom nav
5. Create a post from mobile
6. View Community Board on mobile
7. View Trade Deals on mobile

---

### MESSAGING
1. Click "Messages" in sidebar
2. Start a new conversation or open existing
3. Send a message
4. Verify message appears in real-time
5. Test on two devices if possible (real-time WebSocket test)

---

### POST CREATION
1. Click the "+" or "Create Post" button
2. Enter Title (required)
3. Enter Description (required)
4. Select Category (Goods, Services, or Skills)
5. Add items to "Offering" section
6. Add items to "Looking For" section
7. Upload images (optional)
8. Submit and verify post appears in feed

---

### ADMIN FUNCTIONS (ADMIN ONLY)
1. Go to Admin Dashboard
2. Check "Overview" tab, verify stats load
3. Check "Users" tab, search for users
4. Verify/Unverify a trader badge
5. Check "Posts" tab, view all posts
6. Delete a post if needed
7. Check "Activity Log" for audit trail

---

### SECURITY CHECKS
1. Try accessing admin pages as non-admin (should redirect/deny)
2. Verify you cannot see other users' private messages
3. Verify you cannot delete other users' posts/comments
4. Log out and try accessing protected pages (should redirect to login)

---

### REPORT ANY ISSUES
- Note the exact steps to reproduce
- Screenshot any visual bugs
- Note device/browser used
- Report in designated feedback channel

---

Version: Post-Modular Refactoring Release
Date: April 3, 2026
