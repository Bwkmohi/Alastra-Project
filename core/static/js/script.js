document.getElementById("toggleBtn").addEventListener("click", function() {
    const menu = document.getElementById("extra-menu");
    menu.style.display = menu.style.display === "none" ? "block" : "none";
  });
  
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(() => console.log("Service Worker Registered"));
  }
  
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    deferredPrompt = event;
    document.getElementById("install-btn").style.display = "block";
  });
  
  document.getElementById("install-btn").addEventListener("click", () => {
    deferredPrompt.prompt();
  });