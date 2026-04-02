// Rebel Trade Network - Enhanced Service Worker for PWA
const CACHE_NAME = 'rebel-trade-v1';
const OFFLINE_URL = '/offline.html';

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', function(event) {
  console.log('[SW] Installing Service Worker...');
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log('[SW] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
  console.log('[SW] Service Worker activated');
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.filter(function(cacheName) {
          return cacheName !== CACHE_NAME;
        }).map(function(cacheName) {
          console.log('[SW] Deleting old cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache or network with offline fallback
self.addEventListener('fetch', function(event) {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip API requests - let them fail naturally
  if (event.request.url.includes('/api/')) {
    return;
  }

  // Skip WebSocket connections
  if (event.request.url.includes('ws://') || event.request.url.includes('wss://')) {
    return;
  }

  event.respondWith(
    fetch(event.request).then(function(response) {
      // Cache successful responses for static assets
      if (response.status === 200) {
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          // Only cache same-origin requests
          if (event.request.url.startsWith(self.location.origin)) {
            cache.put(event.request, responseClone);
          }
        });
      }
      return response;
    }).catch(function() {
      // Network failed, try cache
      return caches.match(event.request).then(function(cachedResponse) {
        if (cachedResponse) {
          return cachedResponse;
        }
        // If no cache and navigation request, show offline page
        if (event.request.mode === 'navigate') {
          return caches.match(OFFLINE_URL);
        }
        return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
      });
    })
  );
});

// Push notification event
self.addEventListener('push', function(event) {
  console.log('[SW] Push received:', event);

  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'Rebel Trade Network', body: event.data.text() };
    }
  }

  const title = data.title || 'Rebel Trade Network';
  const options = {
    body: data.body || 'You have a new notification',
    icon: data.icon || '/icons/icon-192x192.png',
    badge: '/icons/icon-96x96.png',
    vibrate: [100, 50, 100],
    data: data.data || {},
    tag: data.data?.type || 'default',
    requireInteraction: true,
    actions: [
      { action: 'open', title: 'Open' },
      { action: 'close', title: 'Dismiss' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Handle notification click
self.addEventListener('notificationclick', function(event) {
  console.log('[SW] Notification clicked:', event.notification.tag);
  event.notification.close();

  const data = event.notification.data || {};
  let url = '/';

  // Navigate based on notification type
  if (data.url) {
    url = data.url;
  } else if (data.type === 'message') {
    url = '/messages';
  } else if (data.type === 'comment' || data.type === 'like') {
    url = '/';
  }

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
      // Focus existing window if available
      for (const client of clientList) {
        if (client.url.includes(self.registration.scope) && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      // Open new window
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});
