# Olamide Olanipekun — Portfolio

Personal portfolio site for **Olamide Olanipekun** (Flux) — Product Manager · Product Builder · Growth & Analytics.

Live: _add your Vercel URL here after the first deploy_

## What this is

A single-file, zero-build static site. Everything — markup, styles, data, and behaviour — lives in `index.html`.
No framework, no bundler, no install step. Open the file in a browser and it runs.

That is a deliberate choice: a portfolio should load instantly, never break because a dependency
moved, and stay editable years from now without archaeology.

## Structure

`index.html` is organised in six labelled blocks:

| Block | What it holds |
| --- | --- |
| `1. DATA` | All content: profile, socials, navigation, metrics, experience, projects, process, skills |
| `2. COMPONENTS` | Pure functions returning HTML — `Navbar`, `Footer`, `Hero`/`Axis`, `SectionHeader`, `ProjectCard`, `ExperienceTimeline`, `SkillGroup`, `MetricCard`, `SocialLinks`, `CTA` |
| `3. PAGES` | The eight pages, composed from components |
| `4. ROUTER` | Hash router, per-page `<title>` |
| `5. BEHAVIOUR` | Theme, mobile nav, scroll reveal, count-up, timeline drawers, hero animation |
| `6. BOOT` | Theme restore, reduced-motion flag, first render |

Content is separated from presentation. To change what the site says, edit the `DATA` block only.

## Editing the content

**Add or change a social link** — one place, `SOCIALS`:

```js
const SOCIALS = {
  email: { label:'Email', value:'flux.fx05@gmail.com', url:'mailto:flux.fx05@gmail.com', icon:'mail', primary:true },
  ...
  website: { label:'Website', value:null, url:null, icon:'globe' }  // inactive until a URL is set
};
```

Entries with `url: null` are skipped everywhere rather than guessed. Set a `url` and add
`primary: true` and it appears in the nav sheet, contact page, résumé, and footer at once.

**Add a role** — push to `EXPERIENCE`. `when: null` renders as "dates not listed" instead of
inventing a date range.

**Add a project** — push to `PROJECTS.others`. The flagship case study is `PROJECTS.fortaflow`.

## Design system

Amber phosphor on graphite — the colourway of early financial data terminals, chosen because the
work sits in trading, analytics, and instrumentation. All tokens are CSS custom properties in
`:root`, with a light theme overriding them under `[data-theme="light"]`.

```
--base    #0E1011   --text    #EDEAE4   --accent  #E5A244
--surface #14171A   --text-2  #B4B7B3   --line    #252A2E
```

`--ff` (`#7C5CFF`) is FortaFlow's own brand violet and is scoped to that case study only.

Type: **Instrument Sans** for everything structural, **IBM Plex Mono** for metrics, dates, and
technical labels. Both from Google Fonts, with system fallbacks if the request fails.

## Accessibility

- Semantic landmarks, one `<h1>` per page, ordered headings
- Skip link, visible `:focus-visible` rings, `aria-current` on the active nav item
- Timeline drawers are real `aria-expanded` / `aria-controls` buttons
- `prefers-reduced-motion` disables the hero sequence, reveals, count-ups, and smooth scroll
- External links carry `rel="noopener noreferrer"` and an "opens in a new tab" hint for screen readers

## Routing

Hash-based (`#/about`), so the site behaves identically from `file://`, GitHub Pages, or Vercel with
no rewrite rules and no chance of a 404 on refresh. `document.title` updates per page.

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` directly also works.

## Verifying before you publish

```bash
node tools/check.js
```

Renders all eight pages in Node against a small DOM shim and asserts: no page throws, exactly one
`<h1>` each, no heading-level skips, no `undefined`/`null`/unresolved `${}` leaking into markup,
every internal `#/` link resolves to a real route, every external link is https with
`rel="noopener"`, résumé links agree with the `PROFILE.resumeReady` flag, every referenced local
asset exists, share images are absolute URLs, one site origin across `index.html` + `robots.txt` +
`sitemap.xml`, and `vercel.json` contains only keys Vercel accepts.

It needs no dependencies and takes about a second. Run it after any content edit.

`tools/make-assets.py` regenerates `og-image.png`, `twitter-card.png` and `apple-touch-icon.png`
from code (Pillow only, no network).

## Deploy

```bash
bash deploy.sh
```

Verifies the site, commits, pushes to the GitHub repo named in `REPO_URL` at the top of the script
(`https://github.com/Flux-web3/Portfolio.git`), deploys to Vercel, then offers to rewrite the site
URL to the real domain. Safe to re-run — a second run just pushes, which is also how you ship an
edit later.

It does not create the repo; that already exists, so it needs only `git` and `node`.
[`gh`](https://cli.github.com) is optional — used only to hand git a credential if it happens to be
installed — and so is `vercel`; if either is missing the script prints the manual steps instead of
failing silently.

Two things it handles for you:

- **The first push may not fast-forward.** If the repo was created with a README, `.gitignore` or
  licence ticked, GitHub already has a commit that this history knows nothing about. The script
  checks before pushing, shows you what is up there, and asks whether to replace it
  (`git push --force-with-lease`), replay this history on top of it
  (`git pull --rebase --allow-unrelated-histories`), or stop. Pressing Enter takes the option that
  throws nothing away; it never force-pushes unless you type `1`.
- **An `origin` that already points somewhere else** is printed next to `REPO_URL` and left alone
  unless you say to change it.

The first push will ask GitHub who you are. If that fails, the script prints the three ways to fix
it — `gh auth login`, a personal access token pasted as the password, or an SSH remote.

Configuration lives in `vercel.json` — static, `cleanUrls`, security headers, immutable asset
caching, and `must-revalidate` on the HTML so edits appear immediately.

### ⚠ The one thing you must not skip

`index.html`, `robots.txt` and `sitemap.xml` ship with a **placeholder origin**
(`https://olamide-olanipekun.vercel.app`). Until it matches the live domain, the `canonical` tag
tells Google the real page lives at a URL that does not exist, and LinkedIn, X, Facebook and Slack
cannot fetch the share image — the card renders blank.

```bash
bash tools/set-site-url.sh https://your-real-domain
git commit -am "Point canonical, og:image and sitemap at the live domain" && git push
```

`deploy.sh` offers to do this for you. `tools/check.js` fails if the three files ever disagree.

Afterwards, re-scrape the card so the platforms drop their cached copy:
[LinkedIn](https://www.linkedin.com/post-inspector/) ·
[Facebook](https://developers.facebook.com/tools/debug/)

### Why the repo is public

The user's instruction was to publish publicly unless the repo holds anything sensitive. It does
not: no `.env`, keys, tokens, or credentials, and the email, links and résumé PDF it contains are
all already published on the website itself, so a private repo would protect nothing. The PDF was
checked for a home address, phone number, date of birth and ID numbers — it contains none.

Note that the *site* does publish a WhatsApp number (the résumé does not). That is a deliberate
reachability-versus-scraping trade-off; to remove it, delete the `whatsapp` entry from `SOCIALS`
and everything referencing it disappears.

## A note on content accuracy

Nothing in this site is invented. Where a fact was not supplied it is either omitted or rendered as a
visible placeholder — Debonk shows "dates not listed" rather than a guessed range, and the metrics
carry an explicit note that they are outcomes contributed to as part of a team, not sole attribution.
FortaFlow is labelled as in active development rather than shipped. Please keep that discipline when
editing.

## Licence

Content and design © 2026 Olamide Olanipekun. Code is free to learn from.
