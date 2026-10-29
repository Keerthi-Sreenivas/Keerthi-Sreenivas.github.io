# keerthi-sreenivas.github.io

Personal site of Keerthi Sreenivas: homepage, writing, talks, projects and Qriosity (curiosity) content, with [Webmentions](https://indieweb.org/Webmention) enabled.

## How it works

- `data/content.json` is the single source of truth (site info, articles, videos, projects, curiosity items).
- `python3 tools/build.py` generates `index.html`, `posts/<slug>/index.html` (one per item, the Webmention target) and `feed.xml`. The deploy workflow runs it too.
- `css/style.css` (orange and black theme, auto light/dark) and `js/main.js` (theme toggle, Webmention display).

### Add a new article, video or project

Add an entry to `items` in `data/content.json` (put new ones first), set `thumb` to an image path or `placeholder` to a short label, run `python3 tools/build.py`, commit.

## Webmentions setup (one-time)

The pages already advertise `<link rel="webmention">` and `rel="pingback"` pointing at webmention.io, and `rel="me"` links to GitHub, LinkedIn and Instagram.

1. Go to <https://webmention.io> and sign in with `https://keerthi-sreenivas.github.io`.
   The sign-in uses the `rel="me"` links, so your GitHub profile's website field must point back to this site.
2. Mentions then appear on each item's page and as counts on the homepage. Sites can send them with the form on each page.
