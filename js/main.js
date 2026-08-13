// Portfolio JS - vanilla, no dependencies
(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ─── Smooth scroll for anchor links ──────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var href = this.getAttribute('href');
      if (href === '#') return;
      var target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // ─── Scroll-reveal with IntersectionObserver ─────────────────
  (function initReveal() {
    var sections = document.querySelectorAll('.reveal');
    if (!sections.length) return;

    if (reducedMotion) {
      sections.forEach(function (el) { el.classList.add('active'); });
      return;
    }

    var revealed = 0;
    var total = sections.length;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          observer.unobserve(entry.target);
          revealed++;
          if (revealed >= total) {
            observer.disconnect();
          }
        }
      });
    }, { threshold: 0.1 });

    sections.forEach(function (section) {
      observer.observe(section);
    });
  })();

  // ─── Typing effect for header name ──────────────────────────
  (function initTyping() {
    var el = document.querySelector('.header-name');
    if (!el) return;

    if (reducedMotion) return;

    var text = el.textContent;
    el.textContent = '';
    el.classList.add('typing-cursor');
    var i = 0;

    function type() {
      if (i < text.length) {
        el.textContent += text.charAt(i);
        i++;
        setTimeout(type, 60 + Math.random() * 40);
      } else {
        // Remove cursor after a short pause
        setTimeout(function () {
          el.classList.remove('typing-cursor');
        }, 1500);
      }
    }

    // Small delay before starting
    setTimeout(type, 400);
  })();

  // ─── Particle canvas background ─────────────────────────────
  (function initCanvas() {
    if (reducedMotion) return;

    var canvas = document.getElementById('bg-canvas');
    if (!canvas) return;

    var ctx = canvas.getContext('2d');
    var particles = [];
    var particleCount = 40;
    var connectionDistance = 120;
    var animId = null;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }

    function createParticle() {
      return {
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 1.5 + 0.5
      };
    }

    function initParticles() {
      particles = [];
      for (var i = 0; i < particleCount; i++) {
        particles.push(createParticle());
      }
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw connections
      for (var i = 0; i < particles.length; i++) {
        for (var j = i + 1; j < particles.length; j++) {
          var dx = particles[i].x - particles[j].x;
          var dy = particles[i].y - particles[j].y;
          var dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionDistance) {
            var opacity = (1 - dist / connectionDistance) * 0.15;
            ctx.beginPath();
            ctx.strokeStyle = 'rgba(167, 139, 250, ' + opacity + ')';
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw and update particles
      for (var k = 0; k < particles.length; k++) {
        var p = particles[k];

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(167, 139, 250, 0.4)';
        ctx.fill();

        // Update position
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around edges
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
      }

      animId = requestAnimationFrame(draw);
    }

    resize();
    initParticles();
    draw();

    window.addEventListener('resize', function () {
      resize();
      // Re-distribute particles that fell outside the new bounds
      for (var i = 0; i < particles.length; i++) {
        if (particles[i].x > canvas.width) particles[i].x = Math.random() * canvas.width;
        if (particles[i].y > canvas.height) particles[i].y = Math.random() * canvas.height;
      }
    });

    // Pause animation when tab is hidden for performance
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        if (animId) {
          cancelAnimationFrame(animId);
          animId = null;
        }
      } else {
        if (!animId) {
          draw();
        }
      }
    });
  })();

})();
