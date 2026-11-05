# Olamide Olanipekun — Portfolio

Personal portfolio site for **Olamide Olanipekun** — product/project management, Web3 community growth, customer support/CX, marketing, operations, analytics and AI-assisted product building.

Live: <https://portfolio-site-kappa-ashy.vercel.app> · Repo: <https://github.com/Flux-web3/Portfolio>.
Pushing `main` publishes it — see [Deploy](#deploy).

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

## Résumé downloads

The Product Manager résumé is `Olamide-Olanipekun-Product-Manager.pdf`, a two-page, ATS-readable PDF.
It retains the full May 2022-Dec 2023 Limitless Prop Firm employer span and does not add the Community
& Customer support specialist as a separate PM résumé role.

The standalone Community Management résumé is `Olamide_Olanipekun_Community_Management_Resume.pdf`,
a two-page A4, ATS-readable PDF. It includes YNX, Deserialize, both concurrent Limitless positions with
their separate LinkedIn dates, Gotabit, and Betboom, plus community skills, tools, selected Web3 projects,
and education. Its reproducible ReportLab source is `tools/build-community-resume.py`. Both résumé PDFs use larger principal text (10.0 pt body and bullets, with summaries at 10.5 pt or above),
flow role content naturally across page breaks, and remain exactly two A4 pages. The validators enforce
page count, A4 dimensions, extractable text, minimum principal type size, and first-page content flow.
GitHub Actions validates both generated PDFs, then publishes changed binaries through a separate
post-validation job on trusted pushes to `main`; pull-request validation remains read-only. The Résumé page links
directly to both PDFs; `community-resume.html` remains available as a browser-based, print-ready
alternative. The two résumé documents are intentionally distinct.

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

**Concurrent positions at one employer** — use `also` and include the secondary title's own date range.
Limitless is the current example: Product Manager & Growth Operations Lead (Sep-Dec 2023) and
Community & Customer support specialist (May 2022-Dec 2023). The Experience timeline shows both;
the PM résumé suppresses the secondary community title and keeps the full May 2022-Dec 2023 employer
span. The standalone Community Management résumé lists both positions.

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

**Pushing `main` deploys to production.** The Vercel project `portfolio-site` (team `flux-build`) is
connected to `Flux-web3/Portfolio`, so every push to `main` builds and goes live at
<https://portfolio-site-kappa-ashy.vercel.app> within seconds. Verified 2026-09-29: commit `79cc01b`
was built by Vercel from GitHub (source `git`, target `production`) with no CLI involved.

```bash
node tools/check.js   # always, before pushing — a push is a production release
git push origin main
```

Then confirm it landed: `vercel ls portfolio-site --scope flux-build` should show the new deployment
as `● Ready`, and the live page should serve the new copy.

`deploy.sh` still works and is handy on a fresh machine:

```bash
bash deploy.sh
```

It verifies the site, commits, pushes to the GitHub repo named in `REPO_URL` at the top of the script
(`https://github.com/Flux-web3/Portfolio.git`), runs `vercel deploy --prod`, then offers to rewrite the
site URL to the real domain. The script predates the Git integration, so its `vercel deploy` step now
duplicates the deployment the push already triggered — harmless (both build the same commit), just
redundant.

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

**Live at https://portfolio-site-kappa-ashy.vercel.app** (Vercel project `portfolio-site`, team
`flux-build` — formerly `forta-flow`, which is why older deployment URLs still end in
`-forta-flow.vercel.app`). `index.html`, `robots.txt` and `sitemap.xml` all carry that origin, so the canonical
tag, `og:image`, `twitter:image` and the sitemap were verified together on 2026-11-05. It previously shipped
with a placeholder that resolved to nothing, which makes the `canonical` tag tell Google the real
page lives at a URL that does not exist and leaves LinkedIn, X, Facebook and Slack unable to fetch
the share image — the card renders blank.

**The trap, if you ever re-point it:** every deployment has two kinds of `https://…vercel.app` URL
(`vercel --prod` prints both; `vercel inspect` lists them) and they are not interchangeable.

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
# the push deploys it — Vercel's GitHub integration builds main automatically
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

- **Experience dates and titles follow the current LinkedIn record supplied by the owner.**
  YNX: Apr 2025 – May 2026; Dextopus: Aug 2025 – Feb 2026; Debonk Bot: Jun 2025 – Jan 2026;
  Deserialize: Apr 2024 – May 2025; Limitless Prop Firm: Product Manager & Growth Operations Lead
  (Sep 2022 – Dec 2023) and Community & Customer support specialist (May 2022 – Dec 2023);
  Gotabit: Feb 2021 – Oct 2022; Betboom: Jan 2020 – Sep 2021. Dextopus and Dextopus Bridge
  are the same engagement and must appear only once under Dextopus. Betboom's approximately
  50,000-member community and typical 5–7-minute response times are supplied by the owner.
- **Debonk has confirmed dates** (Jun 2025 – Jan 2026). Its detail bullets — simplified onboarding,
  reduced beginner friction, demo trading, gamification, and work on the final mini-app design —
  are contributions, not measured outcomes. Do not attach percentages or unprovided metrics.
- **YNX's current public title is Product Manager | Growth Lead.** Its dates are Apr 2025 – May 2026.
  The owner built and owned the community from scratch, sourced moderators for community operations,
  and sourced marketing talent and developers for growth and product delivery. The 30% workflow-
  bottleneck reduction is the current LinkedIn figure; do not substitute the older 50% summary figure.
- **Limitless Prop Firm has two concurrent LinkedIn positions.** Product Manager & Growth Operations
  Lead: Sep 2022 – Dec 2023. Community & Customer support specialist: May 2022 – Dec 2023. The
  Experience timeline shows both; the PM résumé intentionally retains one PM entry with the full
  May 2022 – Dec 2023 employer span, while the Community Management résumé lists both titles.
- **Gotabit and Betboom are separate experience entries.** Gotabit is Feb 2021 – Oct 2022.
  Betboom is Jan 2020 – Sep 2021. Do not list either again as a current freelance/client role.
- **Tourist (TS Academy capstone) is sourced from its Notion Document Hub and the
  `Flux-web3/Tourist-App` repo, nothing else.** It is a travel-planning concept with a working
  browser prototype; itinerary drafts use seeded templates rather than a live AI model. The survey
  numbers (19 usable of 20, 68%, 4.3/5, 4.1/5, 7.3/10) are the hub's. The prototype's itinerary drafts
  come from a seeded template bank, not a language model. The live URL is `tourist-app-blush.vercel.app`;
  the older `tourist-app-nu-six` alias 404s.
- **FortaFlow's coding/build work is currently paused**, and it is not a shipped or production-ready
  system. The public MVP scope is intermediate retail crypto/forex strategy definition, immutable
  versions, reproducible historical backtesting, performance/risk reporting, bounded stress scenarios,
  and manual/CSV journaling. Later and Conditional capabilities are not MVP commitments.
- **The Product Manager PDF is two pages and follows the owner's explicit presentation rule for
  Limitless**: one Product Manager & Growth Operations Lead entry with the full May 2022-Dec 2023
  employer span, and no separate community-only role. The standalone Community Management PDF lists
  both positions with their respective LinkedIn dates; `community-resume.html` remains the browser-based,
  print-ready fallback.

The site labels team outcomes as contributions rather than sole attribution. The Community Management
résumé does not claim community ownership at Deserialize; it describes the verified product and ecosystem
operations work only. FortaFlow is labelled as build-paused, not production-ready. The chronology distinguishes concurrent positions at one
employer and overlapping engagements; calendar time is counted once in experience totals. The
homepage's **All projects** link routes to Experience by design, while individual project cards route
to their project detail page.

The workflow has a read-only validation job that renders all eight SPA pages, checks route/link and asset
integrity, validates site configuration, and generates both résumé PDFs for page, typography, and factual
checks. A separate trusted-main publishing job uses write permission only on pushes to `main`; it commits
updated PDF binaries only when their generated content changes, then validates committed and generated
copies together. Pull-request validation remains read-only. The PDF URLs use revalidation caching because
they have fixed paths.

The 4+ years hands-on product/project management figure is the owner's stated professional positioning;
it is not calculated by adding the durations of overlapping LinkedIn entries. The PM résumé retains
the requested full Limitless employer span, while the Experience timeline shows the Product Manager &
Growth Operations Lead role from Sep 2022 and the separate Community & Customer support specialist role
from May 2022. Concurrent calendar time is counted once. The broader 7+ years spans product, operations,
marketing, growth, community management, customer experience, and trading.

The public education entry lists the B.Sc.Ed. in Mathematics and Education, University of Lagos,
and Second Class Upper. It does not publish a graduation date or CGPA.

## Licence

Content and design © 2026 Olamide Olanipekun. Code is free to learn from.
