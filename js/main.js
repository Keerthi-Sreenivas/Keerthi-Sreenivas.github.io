/* Theme toggle + Webmention.io integration. No dependencies. */
(function () {
  'use strict';

  // ---------- Theme ----------
  var root = document.documentElement;
  var toggle = document.querySelector('.theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var current = root.getAttribute('data-theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      var next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  // ---------- Webmentions (https://webmention.io) ----------
  var API = 'https://webmention.io/api/mentions.jf2';
  var PER_PAGE = 100;

  function norm(url) {
    return String(url || '').replace(/#.*$/, '').replace(/\/+$/, '');
  }

  function fetchMentions(targets) {
    var qs = targets.map(function (t) { return 'target[]=' + encodeURIComponent(t); }).join('&');
    var url = API + '?' + qs + '&per-page=' + PER_PAGE + '&sort-dir=up';
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error('webmention.io responded ' + r.status);
      return r.json();
    }).then(function (j) { return j.children || []; });
  }

  var verbs = {
    'like-of': 'liked this',
    'repost-of': 'reposted this',
    'in-reply-to': 'replied',
    'mention-of': 'mentioned this',
    'bookmark-of': 'bookmarked this'
  };

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  function render(container, mentions) {
    var list = container.querySelector('.wm-list');
    if (!list) return;
    list.textContent = '';
    if (!mentions.length) {
      list.appendChild(el('p', 'wm-status', 'No Webmentions yet. Be the first!'));
      return;
    }
    mentions.forEach(function (m) {
      var author = m.author || {};
      var name = author.name || (m.url ? new URL(m.url).hostname : 'Someone');
      var item = el('article', 'wm-item');
      if (author.photo && /^https:/.test(author.photo)) {
        var img = el('img');
        img.src = author.photo; img.alt = ''; img.loading = 'lazy'; img.width = 44; img.height = 44;
        item.appendChild(img);
      } else {
        item.appendChild(el('span', 'wm-avatar'));
      }
      var body = el('div');
      var who = el('p', 'who', name);
      body.appendChild(who);
      var what = el('p', 'what');
      var verb = verbs[m['wm-property']] || 'mentioned this';
      var link = el('a', null, verb);
      if (m.url && /^https?:/.test(m.url)) { link.href = m.url; link.rel = 'noopener noreferrer ugc'; }
      what.appendChild(link);
      if (m.published) {
        var d = new Date(m.published);
        if (!isNaN(d)) what.appendChild(document.createTextNode(' \u00b7 ' + d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })));
      }
      body.appendChild(what);
      var text = m.content && m.content.text;
      if (text) body.appendChild(el('p', null, text.length > 280 ? text.slice(0, 277) + '\u2026' : text));
      item.appendChild(body);
      list.appendChild(item);
    });
  }

  function init() {
    var containers = [].slice.call(document.querySelectorAll('[data-wm-target]'));
    var badges = [].slice.call(document.querySelectorAll('[data-wm-count]'));
    if (!containers.length && !badges.length) return;

    // One request for everything on the page: the containers plus every badge.
    var all = {};
    containers.forEach(function (c) { all[c.getAttribute('data-wm-target')] = 1; });
    badges.forEach(function (b) { all[b.getAttribute('data-wm-count')] = 1; });
    var targets = [];
    Object.keys(all).forEach(function (t) {
      targets.push(t);
      targets.push(t.replace(/\/$/, '')); // match mentions sent without the trailing slash
    });

    var cacheKey = 'wm:' + location.pathname;
    fetchMentions(targets).then(function (mentions) {
      try { sessionStorage.setItem(cacheKey, JSON.stringify(mentions)); } catch (e) {}
      return mentions;
    }).catch(function () {
      try { return JSON.parse(sessionStorage.getItem(cacheKey)) || null; } catch (e) { return null; }
    }).then(function (mentions) {
      if (!mentions) {
        containers.forEach(function (c) {
          var s = c.querySelector('.wm-status');
          if (s) s.textContent = 'Webmentions could not be loaded right now.';
        });
        return;
      }
      var seen = {};
      var unique = mentions.filter(function (m) {
        var k = m['wm-id'] || m.url + '|' + m['wm-target'];
        if (seen[k]) return false; seen[k] = 1; return true;
      });
      containers.forEach(function (c) {
        var t = norm(c.getAttribute('data-wm-target'));
        render(c, unique.filter(function (m) { return norm(m['wm-target']) === t; }));
      });
      badges.forEach(function (b) {
        var t = norm(b.getAttribute('data-wm-count'));
        var n = unique.filter(function (m) { return norm(m['wm-target']) === t; }).length;
        if (n > 0) {
          b.textContent = n + (n === 1 ? ' Webmention' : ' Webmentions');
          b.hidden = false;
        }
      });
    });
  }

  init();
})();
