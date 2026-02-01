self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('app-cache').then(cache => {
      return cache.addAll([
        '/',
        '/static/js/script.js',
        '/static/js/manifest.json',
        '/static/img/icon.png'
      ]);
    })
  );
});