const CACHE = "tabi-v3";
const BASE = new URL("./", self.location).pathname;  /* 置き場所が変わっても壊れない */
const URLS = [BASE, BASE + "index.html", BASE + "manifest.json", BASE + "icon-192.png", BASE + "icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(URLS)).then(() => self.skipWaiting()));
});

/* 同じオリジンに麻雀アプリが同居している。消すのは自分の古いキャッシュ（tabi-）だけ */
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith("tabi-") && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

/* 画面はネットワーク優先（更新をすぐ反映）／それ以外はキャッシュ優先 */
self.addEventListener("fetch", e => {
  if (e.request.mode === "navigate") {
    e.respondWith(
      fetch(e.request).then(res => {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(BASE + "index.html", clone));
        return res;
      }).catch(() => caches.match(BASE + "index.html"))
    );
    return;
  }
  e.respondWith(caches.match(e.request).then(cached => {
    if (cached) return cached;
    return fetch(e.request).then(res => {
      if (res && res.status === 200) {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
      }
      return res;
    }).catch(() => caches.match(BASE + "index.html"));
  }));
});
