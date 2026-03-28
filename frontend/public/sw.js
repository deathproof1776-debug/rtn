// HomesteadHub Service Worker for Push Notifications

// Listen for push events
self.addEventListener('push', function(event) {
  console.log('[SW] Push received:', event);

  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'HomesteadHub', body: event.data.text() };
    }
  }

  const title = data.title || 'HomesteadHub';
  const options = {
    body: data.body || 'You have a new notification',
    icon: data.icon || '/logo192.png',
    badge: '/logo192.png',
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

// Service worker activation
self.addEventListener('activate', function(event) {
  console.log('[SW] Service Worker activated');
  event.waitUntil(self.clients.claim());
});

// Service worker installation
self.addEventListener('install', function(event) {
  console.log('[SW] Service Worker installed');
  self.skipWaiting();
});
