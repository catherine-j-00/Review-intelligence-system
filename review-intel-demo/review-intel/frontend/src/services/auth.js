const KEY = 'token';

// Clear the login when the page was really left (Leave / new URL),
// but keep it on a refresh.
(function () {
  try {
    const nav = performance.getEntriesByType('navigation')[0];
    if (sessionStorage.getItem('leaving') && !(nav && nav.type === 'reload')) {
      sessionStorage.removeItem(KEY);
    }
    sessionStorage.removeItem('leaving');
  } catch { /* ignore */ }
})();

window.addEventListener('pagehide', () => {
  try { sessionStorage.setItem('leaving', '1'); } catch { /* ignore */ }
});

// If Chrome restores the page from its back/forward cache after the user
// left it, treat that as a fresh visit: drop the login.
window.addEventListener('pageshow', (e) => {
  try {
    if (e.persisted && sessionStorage.getItem('leaving')) {
      sessionStorage.removeItem(KEY);
      sessionStorage.removeItem('leaving');
    }
  } catch { /* ignore */ }
});

// True only if a token exists AND has not expired.
// Removes the token if it is expired or malformed.
export function isAuthenticated() {
  const token = sessionStorage.getItem(KEY);
  if (!token) return false;
  try {
    const payload = JSON.parse(
      atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))
    );
    if (payload.exp && payload.exp * 1000 <= Date.now()) {
      sessionStorage.removeItem(KEY);
      return false;
    }
    return true;
  } catch {
    sessionStorage.removeItem(KEY);
    return false;
  }
}