#!/usr/bin/env python3
"""Static site generator for keerthi-sreenivas.github.io.

Reads data/content.json and writes:
  index.html                  the homepage
  posts/<slug>/index.html     one page per item (the Webmention target)
  feed.xml                    Atom feed

Usage: python3 tools/build.py
No dependencies beyond the Python standard library.
"""
import json
import os
import zlib
from datetime import datetime
from html import escape as e
from xml.sax.saxutils import escape as xe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "data", "content.json"), encoding="utf-8") as f:
    DATA = json.load(f)

SITE = DATA["site"]
ITEMS = DATA["items"]
BASE = SITE["url"].rstrip("/")
WM_ENDPOINT = "https://webmention.io/%s/webmention" % SITE["domain"]
PINGBACK = "https://webmention.io/%s/xmlrpc" % SITE["domain"]

SUN = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'


def permalink(item):
    return "%s/posts/%s/" % (BASE, item["slug"])


def fmt_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def head(title, desc, canonical, prefix, og_image=None, og_type="website"):
    img = og_image or "%s/images/me_.jpg" % BASE
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#111111">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{img}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%23111'/%3E%3Ctext x='50' y='72' font-size='64' font-family='Georgia,serif' font-weight='700' text-anchor='middle' fill='%23ff6a00'%3EK%3C/text%3E%3C/svg%3E">
  <link rel="alternate" type="application/atom+xml" title="Keerthi Sreenivas" href="{prefix}feed.xml">
  <!-- Webmention.io: receive Webmentions and Pingbacks for this site -->
  <link rel="webmention" href="{wm}">
  <link rel="pingback" href="{pb}">
  <!-- IndieWeb identity (also used to sign in to webmention.io) -->
  <link rel="me" href="{gh}">
  <link rel="me" href="{li}">
  <link rel="me" href="{ig}">
  <script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
  <link rel="stylesheet" href="{prefix}css/style.css">
</head>
""".format(title=e(title), desc=e(desc), canonical=canonical, og_type=og_type, img=img,
           prefix=prefix, wm=WM_ENDPOINT, pb=PINGBACK, gh=SITE["github"],
           li=SITE["linkedin"], ig=SITE["instagram"])


def header(prefix):
    home = prefix or "./"
    return """<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{home}">Keerthi Sreenivas</a>
    <nav aria-label="Main">
      <a href="{home}#writing">Writing</a>
      <a href="{home}#videos">Videos</a>
      <a href="{home}#projects">Projects</a>
      <a href="{home}#curiosity">Curiosity</a>
      <a href="{home}#newsletter">Newsletter</a>
      <a href="{home}#elsewhere">Elsewhere</a>
      <button class="theme-toggle" type="button" aria-label="Toggle light and dark theme">{sun}</button>
    </nav>
  </div>
</header>
""".format(home=home, sun=SUN)


def footer(prefix):
    return """<footer class="site-footer">
  <div class="wrap">
    <p>&copy; {year} Keerthi Sreenivas. Built by hand, with <a href="https://www.w3.org/TR/webmention/" rel="noopener noreferrer" target="_blank">Webmentions</a> turned on.</p>
    <p class="small"><a href="{p}feed.xml">Feed</a> &middot; <a rel="me noopener noreferrer" target="_blank" href="{gh}">GitHub</a> &middot; <a rel="me noopener noreferrer" target="_blank" href="{li}">LinkedIn</a> &middot; <a rel="me noopener noreferrer" target="_blank" href="{ig}">Instagram</a></p>
  </div>
</footer>
<script src="{p}js/main.js"></script>
</body>
</html>
""".format(year=datetime.now().year, p=prefix, gh=SITE["github"], li=SITE["linkedin"], ig=SITE["instagram"])


def thumb(item, prefix, size="card"):
    if item.get("thumb"):
        return '<img class="u-photo" src="%s%s" alt="" loading="lazy" width="640" height="360">' % (prefix, e(item["thumb"]))
    label = item.get("placeholder") or item["title"][:3]
    return '<span class="ph" role="img" aria-label="Thumbnail placeholder"><span>%s</span></span>' % e(label)


def byline(item):
    when = ""
    if item.get("date"):
        when = ' on <time class="dt-published" datetime="%s">%s</time>' % (item["date"], fmt_date(item["date"]))
    return 'Posted%s by <span class="p-author h-card">Keerthi Sreenivas</span> in <span class="p-category">%s</span>' % (when, e(item["category"]))


def wm_badge(item):
    return '<span class="wm-count" data-wm-count="%s" hidden></span>' % permalink(item)


def feed_item(item, prefix):
    return """    <li class="h-entry">
      <a class="thumb" href="{p}posts/{slug}/" tabindex="-1" aria-hidden="true">{thumb}</a>
      <div class="body">
        <p class="meta">{by}</p>
        <h3 class="p-name"><a class="u-url" href="{p}posts/{slug}/">{title}</a></h3>
        <p class="p-summary">{excerpt}</p>
        <p class="foot">{wm}<a class="more" href="{p}posts/{slug}/">Details &amp; Webmentions</a></p>
      </div>
    </li>
""".format(p=prefix, slug=item["slug"], thumb=thumb(item, prefix), by=byline(item),
           title=e(item["title"]), excerpt=e(item["excerpt"]), wm=wm_badge(item))


def card(item, prefix):
    return """    <li class="h-entry">
      <a class="thumb" href="{p}posts/{slug}/" tabindex="-1" aria-hidden="true">{thumb}</a>
      <h3 class="p-name"><a class="u-url" href="{p}posts/{slug}/">{title}</a></h3>
      <p class="p-summary">{excerpt}</p>
      <p class="foot">{wm}<span class="cat">{cat}</span></p>
    </li>
""".format(p=prefix, slug=item["slug"], thumb=thumb(item, prefix), title=e(item["title"]),
           excerpt=e(item["excerpt"]), wm=wm_badge(item), cat=e(item["category"]))


def by_cat(*cats):
    return [i for i in ITEMS if i["category"] in cats]


def build_index():
    p = ""
    url = BASE + "/"
    out = head("Keerthi Sreenivas | Solutions Architect & Creator", SITE["description"], url, p)
    out += header(p)
    out += """<main id="main" class="h-card">
  <section class="hero wrap">
    <div class="hero-text">
      <p class="eyebrow">Solutions Architect &middot; Creator &middot; Mentor</p>
      <h1>Hi, I&rsquo;m <span class="p-name">Keerthi Sreenivas</span>.</h1>
      <p class="lead"><span class="p-note">I&rsquo;m a Specialist Solutions Architect for Agentic AI at <a class="u-org" href="https://aws.amazon.com" target="_blank" rel="noopener noreferrer">AWS</a>, working with <strong>Kiro</strong>, <strong>AgentCore</strong> and the <strong>Strands SDK</strong>. I also create: I run <strong>Qriosity</strong>, a curious community of 20K+ AI learners, and I write, speak and build in the open.</span></p>
      <p>This site is my home on the web. Everything I publish elsewhere, from articles and talks to side projects and the Qriosity content, lands here first, and you can reply to any of it with a <a href="#webmentions">Webmention</a>.</p>
      <p class="cta">
        <a class="btn" href="#writing">Read the latest</a>
        <a class="btn ghost" href="{topmate}" target="_blank" rel="noopener noreferrer">Book a mentoring session</a>
      </p>
      <p class="loc"><span class="p-locality">{loc}</span> &middot; <a class="u-url u-uid" href="{url}">{domain}</a></p>
    </div>
    <div class="hero-photo">
      <img class="u-photo" src="images/me_.jpg" alt="Portrait of Keerthi Sreenivas" width="480" height="480">
    </div>
  </section>
""".format(topmate=SITE["topmate"], loc=e(SITE["location"]), url=url, domain=SITE["domain"])

    # Writing
    out += """  <section id="writing" class="wrap">
    <div class="sec-head"><h2>Latest writing</h2><p>Articles on agentic AI, developer tooling and cloud.</p></div>
    <ul class="feed">
"""
    for it in by_cat("Articles"):
        out += feed_item(it, p)
    out += """    </ul>
  </section>

  <section id="videos" class="wrap">
    <div class="sec-head"><h2>Videos &amp; talks</h2><p>Live demos, conference sessions and community talks.</p></div>
    <ul class="grid">
"""
    for it in by_cat("Videos", "Talks"):
        out += card(it, p)
    out += """    </ul>
  </section>

  <section id="projects" class="wrap">
    <div class="sec-head"><h2>Projects</h2><p>Things I&rsquo;ve built to learn something new.</p></div>
    <ul class="grid">
"""
    for it in by_cat("Projects"):
        out += card(it, p)
    out += """    </ul>
  </section>

  <section id="curiosity" class="wrap">
    <div class="sec-head"><h2>Curiosity</h2><p>Qriosity is where the creator side of me lives: short-form AI content and a community that learns together.</p></div>
    <ul class="grid">
"""
    for it in by_cat("Curiosity"):
        out += card(it, p)
    out += """    </ul>
  </section>

  <section id="newsletter" class="wrap">
    <div class="soon">
      <p class="badge">Coming soon</p>
      <h2>Articles &amp; newsletter</h2>
      <p>I&rsquo;ll be writing a lot more long-form articles and starting a newsletter on agentic AI, building with Kiro, and what I&rsquo;m learning along the way. Nothing to sign up for yet. For now, follow along on <a href="{li}" target="_blank" rel="noopener noreferrer">LinkedIn</a> or <a href="{ig}" target="_blank" rel="noopener noreferrer">Instagram</a>, or grab the <a href="feed.xml">feed</a>.</p>
    </div>
  </section>

  <section id="elsewhere" class="wrap">
    <div class="sec-head"><h2>Community &amp; elsewhere</h2></div>
    <ul class="links">
""".format(li=SITE["linkedin"], ig=SITE["instagram"])
    for label, href, _ in DATA["community"]:
        out += '      <li><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>\n' % (e(href), e(label))
    out += """    </ul>
  </section>

  <section id="webmentions" class="wrap wm" data-wm-target="{url}">
    <div class="sec-head"><h2>Webmentions</h2><p>This homepage accepts <a href="https://indieweb.org/Webmention" target="_blank" rel="noopener noreferrer">Webmentions</a>. Link to it from your own site, then send the URL of your post below. Mentions of any article, video or project here show up on that item&rsquo;s page and on the list above.</p></div>
    <div class="wm-list" aria-live="polite"><p class="wm-status">Loading Webmentions&hellip;</p></div>
    {form}
  </section>
</main>
""".format(url=url, form=wm_form(url))
    out += footer(p)
    write("index.html", out)


def wm_form(target):
    return """<form class="wm-form" action="{ep}" method="post" target="_blank" rel="noopener">
      <label for="wm-source-{n}">Wrote about this? Send me a Webmention:</label>
      <div class="row">
        <input id="wm-source-{n}" name="source" type="url" required placeholder="https://your-site.com/your-post">
        <input name="target" type="hidden" value="{t}">
        <button class="btn" type="submit">Send</button>
      </div>
    </form>""".format(ep=WM_ENDPOINT, t=target, n=zlib.crc32(target.encode()) % 100000)


def build_post(item):
    p = "../../"
    url = permalink(item)
    thumb_abs = (BASE + "/" + item["thumb"]) if item.get("thumb") else None
    out = head("%s | Keerthi Sreenivas" % item["title"], item["excerpt"], url, p, thumb_abs, "article")
    out += header(p)
    extras = "".join(' <a class="btn ghost" href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (e(h), e(l)) for l, h in item.get("extra", []))
    out += """<main id="main" class="wrap post h-entry">
  <p class="meta">{by}</p>
  <h1 class="p-name">{title}</h1>
  <p class="lead p-summary">{excerpt}</p>
  <figure class="hero-thumb">{thumb}</figure>
  <p class="cta"><a class="btn u-syndication" href="{orig}" target="_blank" rel="noopener noreferrer syndication">{cta} &rarr;</a>{extras}</p>
  <p class="small">Permalink: <a class="u-url" href="{url}">{url}</a></p>

  <section id="webmentions" class="wm" data-wm-target="{url}">
    <div class="sec-head"><h2>Webmentions</h2></div>
    <div class="wm-list" aria-live="polite"><p class="wm-status">Loading Webmentions&hellip;</p></div>
    {form}
    <p class="small">Webmentions are replies, likes and reposts from other sites. Powered by <a href="https://webmention.io" target="_blank" rel="noopener noreferrer">webmention.io</a>.</p>
  </section>
  <p><a href="{p}#writing">&larr; Back to the homepage</a></p>
</main>
""".format(by=byline(item), title=e(item["title"]), excerpt=e(item["excerpt"]),
           thumb=thumb(item, p), orig=e(item["url"]), cta=e(item["cta"]), extras=extras,
           url=url, form=wm_form(url), p=p)
    out += footer(p)
    write("posts/%s/index.html" % item["slug"], out)


def build_feed():
    now = max(i.get("date", "2026-01-01") for i in ITEMS) + "T00:00:00Z"
    xml = ['<?xml version="1.0" encoding="utf-8"?>',
           '<feed xmlns="http://www.w3.org/2005/Atom">',
           "  <title>Keerthi Sreenivas</title>",
           '  <link href="%s/feed.xml" rel="self"/>' % BASE,
           '  <link href="%s/"/>' % BASE,
           "  <id>%s/</id>" % BASE,
           "  <updated>%s</updated>" % now,
           "  <author><name>Keerthi Sreenivas</name></author>"]
    for it in ITEMS:
        upd = (it.get("date") or "2026-01-01") + "T00:00:00Z"
        xml += ["  <entry>",
                "    <title>%s</title>" % xe(it["title"]),
                '    <link href="%s"/>' % permalink(it),
                "    <id>%s</id>" % permalink(it),
                "    <updated>%s</updated>" % upd,
                "    <category term=\"%s\"/>" % xe(it["category"]),
                "    <summary>%s</summary>" % xe(it["excerpt"]),
                "  </entry>"]
    xml.append("</feed>")
    write("feed.xml", "\n".join(xml) + "\n")


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    build_index()
    for it in ITEMS:
        build_post(it)
    build_feed()
    print("Built index.html, %d post pages and feed.xml" % len(ITEMS))
