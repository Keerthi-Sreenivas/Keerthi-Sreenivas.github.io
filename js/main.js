// Minimal JS - theme toggle only
(function () {
  const html = document.documentElement;
  const stored = localStorage.getItem('theme');

  if (stored === 'light') {
    html.classList.remove('dark');
    html.classList.add('light');
  }
})();
