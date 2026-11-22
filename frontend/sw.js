const CACHE_NAME = 'digest-v13';
const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap'
];

// Install — pre-cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('SW: some assets failed to cache during install:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate — immediately wipe all older caches (including digest-v1) and claim clients
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => {
          console.log('SW: Purging old cache:', k);
          return caches.delete(k);
        })
      )
    )
  );
  self.clients.claim();
});

// Fetch — Network-First for HTML navigation and digest.json; Cache-First for static assets
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Force bypass cache if query param has ?nocache or ?v=
  if (url.searchParams.has('nocache') || url.searchParams.has('v')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Network-first for navigation requests, index.html, root, and digest.json (always get newest content)
  if (
    event.request.mode === 'navigate' ||
    url.pathname.endsWith('index.html') ||
    url.pathname.endsWith('/Daily-Digest/') ||
    url.pathname.endsWith('/Daily-Digest') ||
    url.pathname.endsWith('/') ||
    url.pathname.endsWith('digest.json')
  ) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          // Offline fallback
          return caches.match(event.request).then(cached => {
            if (cached) return cached;
            if (event.request.mode === 'navigate' || url.pathname.endsWith('index.html')) {
              return caches.match('./index.html') || caches.match('./');
            }
            return new Response('Offline', { status: 503, statusText: 'Offline' });
          });
        })
    );
    return;
  }

  // Cache-first for images, fonts, styles
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        if (response.ok && event.request.method === 'GET') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      });
    })
  );
});

// Notification click — focus app or open new window
self.addEventListener('notificationclick', event => {
  event.notification.close();
  const urlToOpen = (event.notification.data && event.notification.data.url) || './';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      for (const client of clientList) {
        if (client.url && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Push event fallback (Web Push API)
self.addEventListener('push', event => {
  let data = { title: '☕ Morning News Digest', body: 'New cybersecurity stories are ready for you.' };
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }
  event.waitUntil(
    self.registration.showNotification(data.title || '☕ Morning News Digest', {
      body: data.body,
      icon: 'icon-192.png',
      badge: 'icon-192.png',
      tag: 'morning-digest',
      data: { url: data.url || './' }
    })
  );
});
