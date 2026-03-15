const CACHE_NAME = 'mindhaven-v1';
const STATIC_CACHE = 'mindhaven-static-v1';
const DYNAMIC_CACHE = 'mindhaven-dynamic-v1';
const API_CACHE = 'mindhaven-api-v1';

// Assets to cache on install
const staticAssets = [
  '/',
  '/offline/',
  '/static/css/style.css',
  '/static/css/sidebar.css',
  '/static/js/main.js',
  '/static/js/auth.js',
  '/static/js/validation.js',
  '/static/js/flash-messages.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(staticAssets))
      .then(() => self.skipWaiting())
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== STATIC_CACHE && key !== DYNAMIC_CACHE && key !== API_CACHE)
          .map(key => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - cache strategies
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // API requests - Network first, then cache (stale-while-revalidate)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clonedResponse = response.clone();
          caches.open(API_CACHE).then(cache => {
            cache.put(event.request, clonedResponse);
          });
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
    return;
  }
  
  // Static assets - Cache first, then network
  if (event.request.url.match(/\.(css|js|png|jpg|jpeg|svg|ico)$/)) {
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
    return;
  }
  
  // HTML pages - Network first, fallback to cache, then offline page
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clonedResponse = response.clone();
          caches.open(DYNAMIC_CACHE).then(cache => {
            cache.put(event.request, clonedResponse);
          });
          return response;
        })
        .catch(() => {
          return caches.match(event.request)
            .then(cached => cached || caches.match('/offline/'));
        })
    );
    return;
  }
  
  // Default - network first
  event.respondWith(
    fetch(event.request)
      .catch(() => caches.match(event.request))
  );
});

// Background sync for offline messages
self.addEventListener('sync', event => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }
});

async function syncMessages() {
  try {
    const db = await openDB();
    const offlineMessages = await getOfflineMessages(db);
    
    for (const message of offlineMessages) {
      await fetch('/api/chat/send/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(message)
      });
      await deleteOfflineMessage(db, message.id);
    }
  } catch (error) {
    console.log('Background sync failed:', error);
  }
}