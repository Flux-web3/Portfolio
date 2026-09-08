# Olamide Olanipekun — Portfolio

Personal portfolio site for **Olamide Olanipekun** (Flux) — Technical Product Manager · Product Builder · Growth & Operations.

Live: <https://github.com/Flux-web3/Portfolio> — replace this with the Vercel URL, then run
`bash tools/set-site-url.sh <that-url>` so `index.html`, `robots.txt` and `sitemap.xml` agree.
`check.js` fails while they disagree.

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
| `2. COMPONENTS` | Pure functions returning HTML — `Navbar`, `Footer`, `Rail`, `PageHead`, `Axis`, `SectionHeader`, `ProjectCard`, `ExperienceTimeline`, `ArchRows`, `ClientList`, `CertList`, `Metrics`, `SocialLinks`, `CTA` |
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

**Add a role** — push to `EXPERIENCE`. `when: null` renders a visible "dates not listed" pill on
both the timeline and the résumé instead of inventing a date range.

**Concurrent titles in one engagement** — use `also`. It renders on the same line in lower emphasis,
so a reader sees every title held and can tell they ran at once rather than as promotions. Used by
YNX and Limitless Prop. Deliberately *not* accent-coloured and not 600 weight: accent is what marks
"this is the job title", so a second title in the same treatment reads as one long invented title.

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
`sitemap.xml`, and `vercel.json` contains only keys Vercel accepts. It also enforces the rule that
the phone number may only ever render inside a `wa.me` anchor — never as a `tel:` link and never as
bare text a scraper can lift.

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

### Three couplings that will bite you

These are all one-line changes that break something 1500 lines away, so they are written here as
well as in comments at each site.

1. **`.sheet` must stay a sibling of `<header>`, never a child.** `.topbar` carries a
   `backdrop-filter`, and an element with a backdrop-filter becomes a containing block for its
   fixed-position descendants — the same rule as `transform` and `filter`. Nested inside, the
   sheet's `inset` resolved against the 64px header rather than the viewport, so it opened at zero
   height and the mobile menu appeared to do nothing. The JS was never at fault.
2. **`--topbar-h` must equal the header height.** The sheet is offset by exactly this token. It used
   to be `64px` hardcoded in both `.topbar-in` and `.sheet`, which is how an unrelated header tweak
   leaves a strip of page content showing above the open menu.
3. **In `.tl-role`, render `.tl-meta` before `.tl-also`.** `.tl-also` is `display:block`, so anything
   after it starts a new line. `.tl-meta`'s `border-left` is a separator meant to sit inline after
   the role; pushed onto its own line it reads as a stray indented tick.

### ⚠ The origin: done, but here is the trap

**Live at https://portfolio-site-kappa-ashy.vercel.app** (Vercel project `portfolio-site`, scope
`forta-flow`). `index.html`, `robots.txt` and `sitemap.xml` all carry that origin, so the canonical
tag, `og:image`, `twitter:image` and the sitemap are correct as of 2026-09-08. It previously shipped
with a placeholder that resolved to nothing, which makes the `canonical` tag tell Google the real
page lives at a URL that does not exist and leaves LinkedIn, X, Facebook and Slack unable to fetch
the share image — the card renders blank.

**The trap, if you ever re-point it:** `vercel --prod` prints two `https://…vercel.app` URLs and they
are not interchangeable.

| Vercel calls it | Example | Use it for |
|---|---|---|
| `Production` | `portfolio-site-hjwym4ui7-forta-flow.vercel.app` | nothing durable — the middle segment is regenerated on **every** deploy |
| `Aliased` | `portfolio-site-kappa-ashy.vercel.app` | the canonical origin, sharing, your CV — it survives deploys |

Canonicalising the `Production` URL is a slow-acting bug: correct on the day you ship, pointing at a
dead build from then on, with the sitemap and both share images inheriting the rot. `deploy.sh` now
reads both and always prefers the alias.

```bash
bash tools/set-site-url.sh https://your-real-domain   # the ALIAS, or a custom domain
git commit -am "Point canonical, og:image and sitemap at the live domain" && git push
vercel --prod   # the push alone does NOT redeploy: this project has no git integration
```

`deploy.sh` offers to do all of this for you. `tools/check.js` fails if the three files ever disagree.

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

Nothing in this site is invented. Specifics worth knowing before you edit:

- **Debonk carries no dates, on purpose.** He asked for them to be left out, so it renders the
  "dates not listed" placeholder. Its detail bullets — simplified onboarding, removed beginner
  friction, the demo trading feature, gamification, sign-off on the final mini-app design — are
  *contributions*, not measurements, because that is how they were supplied. Do not later attach a
  percentage to any of them.
- **YNX's `also` titles (VP Operations, Marketing Lead) came from him directly.** His public LinkedIn
  lists that engagement as "Product Manager · Part-time" only, so a reader checking the profile will
  not find them. Worth adding there if the profile is the reference anyone checks.
- **delabz, Dextopus, Deserialize, YNX and FortaFlow dates were verified** against screenshots of the
  LinkedIn profile and match. Limitless Prop and Debonk were not visible in those captures.

 Where a fact was not supplied it is either omitted or rendered as a
visible placeholder, and the metrics carry an explicit note that they are outcomes contributed to as
part of a team, not sole attribution. FortaFlow is labelled as in active development rather than
shipped. Limitless Prop keeps its `2023 – 2024` range because no start month was supplied — a guessed
month would have made the "4+ years" arithmetic look tidier than the evidence supports. Please keep
that discipline when editing.

Two claims are load-bearing and are worth re-checking whenever the timeline changes. The **7+ years**
figure rests on contract work running back to 2019 (`CLIENTS.note`). The **4+ years** product figure
is *not* derivable from the timeline alone: overlapping roles do not add calendar time, so the union
of the product-titled ranges is only 2.3–3.5 years, and the balance comes from the contract product
work. The arithmetic is written out in a comment above `CONCURRENCY` in `index.html`; do not raise
either number without extending one of those date ranges. Debonk is a seventh product-titled role
and adds nothing to the sum, because it has no dates.

## Licence

Content and design © 2026 Olamide Olanipekun. Code is free to learn from.
