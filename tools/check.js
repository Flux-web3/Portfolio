/* Renders every page of index.html in Node against a minimal DOM shim, then
   checks the produced markup. Catches: runtime throws in page functions,
   `undefined` leaking into output, h1 count, heading-level skips, unresolved
   template placeholders, and links pointing at nothing.
   Run:  node tools/check.js                                                  */
const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, '..', 'index.html');
const html = fs.readFileSync(file, 'utf8');

/* --- a DOM shim just deep enough for module-level code to execute ---------- */
const noop = () => {};
const el = () => new Proxy(function () {}, {
  get(t, k) {
    if (k === 'classList') return { add: noop, remove: noop, toggle: noop, contains: () => false };
    if (k === 'style') return {};
    if (k === 'dataset') return {};
    if (k === 'children' || k === 'childNodes') return [];
    if (k === 'textContent' || k === 'innerHTML' || k === 'value') return '';
    if (k === Symbol.toPrimitive || k === 'toString') return () => '';
    return el();
  },
  set: () => true,
  apply: () => el()
});

global.window = new Proxy({}, {
  get(t, k) {
    if (k === 'matchMedia') return () => ({ matches: false, addEventListener: noop, addListener: noop });
    if (k === 'location') return { hash: '#/', pathname: '/', href: 'http://localhost/' };
    if (k === 'requestAnimationFrame') return noop;
    if (k === 'addEventListener' || k === 'removeEventListener' || k === 'scrollTo') return noop;
    if (k === 'IntersectionObserver') return class { observe() {} unobserve() {} disconnect() {} };
    if (k === 'getComputedStyle') return () => ({ getPropertyValue: () => '' });
    return el();
  },
  set: () => true
});
global.document = new Proxy({}, {
  get(t, k) {
    if (k === 'querySelectorAll' || k === 'getElementsByTagName') return () => [];
    if (k === 'querySelector' || k === 'getElementById') return () => el();
    if (k === 'addEventListener' || k === 'removeEventListener') return noop;
    if (k === 'createElement') return () => el();
    if (k === 'title') return '';
    return el();
  },
  set: () => true
});
global.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
global.requestAnimationFrame = noop;
global.matchMedia = () => ({ matches: false, addEventListener: noop, addListener: noop });
global.location = { hash: '#/', pathname: '/' };
global.navigator = { userAgent: 'node' };

/* --- pull the main script block and expose its page functions -------------- */
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const js = blocks.reduce((a, b) => (b.length > a.length ? b : a), '');

const PAGES = ['Home', 'About', 'Experience', 'Projects', 'Thinking', 'Skills', 'Resume', 'Contact'];
let mod;
try {
  mod = new Function(js + `\nreturn { ${PAGES.join(',')}, NAV, PROFILE, SOCIALS, CERTS, EXPERIENCE, CLIENTS, EDUCATION, routes: typeof ROUTES!=='undefined'?ROUTES:null };`)();
} catch (e) {
  console.error('FATAL: module body threw:', e.message);
  process.exit(1);
}

let fails = 0;
const fail = (...a) => { fails++; console.log('  FAIL', ...a); };

console.log('Rendering ' + PAGES.length + ' pages\n');
const rendered = {};
for (const name of PAGES) {
  let out;
  try { out = mod[name](); } catch (e) { fail(name + ' threw:', e.message); continue; }
  rendered[name] = out;

  const h1 = (out.match(/<h1[\s>]/g) || []).length;
  if (h1 !== 1) fail(`${name}: expected exactly 1 <h1>, found ${h1}`);

  if (/undefined/.test(out)) {
    const ctx = out.match(/.{0,60}undefined.{0,60}/)[0].replace(/\s+/g, ' ');
    fail(`${name}: "undefined" in output → …${ctx}…`);
  }
  if (/\bnull\b/.test(out)) {
    const ctx = out.match(/.{0,60}\bnull\b.{0,60}/)[0].replace(/\s+/g, ' ');
    fail(`${name}: "null" in output → …${ctx}…`);
  }
  if (/\$\{/.test(out)) fail(`${name}: unresolved \${} placeholder`);
  if (/\[object Object\]/.test(out)) fail(`${name}: [object Object] in output`);

  // heading levels must not skip (h1 -> h3 with no h2 between)
  const levels = [...out.matchAll(/<h([1-6])[\s>]/g)].map(m => +m[1]);
  let prev = 0;
  for (const l of levels) {
    if (prev && l > prev + 1) { fail(`${name}: heading skip h${prev} → h${l}`); break; }
    prev = l;
  }
  console.log(`  ${name.padEnd(11)} ${String(out.length).padStart(6)} chars  h1:${h1}  headings:${levels.length}`);
}

/* --- homepage résumé CTA must open the résumé selection page --------------- */
const homeCtaText = '>Download Resume';
const homeCtaTextIndex = rendered.Home?.indexOf(homeCtaText) ?? -1;
if (homeCtaTextIndex < 0) {
  fail('Home: missing Download Resume CTA');
} else {
  const anchorStart = rendered.Home.lastIndexOf('<a', homeCtaTextIndex);
  const anchorEnd = rendered.Home.indexOf('</a>', homeCtaTextIndex);
  const homeResumeCta = rendered.Home.slice(anchorStart, anchorEnd + 4);
  if (!homeResumeCta.includes('href="#/resume"'))
    fail('Home: Download Resume must navigate to #/resume');
  if (homeResumeCta.includes(' download') || homeResumeCta.includes('\\ndownload'))
    fail('Home: Download Resume must not directly download a PDF');
}

/* --- internal hash links must resolve to a real route --------------------- */
const validPaths = new Set(mod.NAV.map(n => n.path));
const bad = new Set();
for (const [name, out] of Object.entries(rendered)) {
  for (const m of out.matchAll(/href="#(\/[a-z-]*)"/g)) {
    if (!validPaths.has(m[1])) bad.add(`${name} → #${m[1]}`);
  }
}
if (bad.size) { fails++; console.log('\n  FAIL unknown internal routes:', [...bad].join(', ')); }

/* --- every external link must be https, and carry rel=noopener ------------- */
for (const [name, out] of Object.entries(rendered)) {
  for (const m of out.matchAll(/<a[^>]+href="(https?:[^"]+)"[^>]*>/g)) {
    if (m[1].startsWith('http://')) fail(`${name}: insecure http link ${m[1]}`);
    if (/target="_blank"/.test(m[0]) && !/rel="noopener/.test(m[0]))
      fail(`${name}: target=_blank without rel=noopener → ${m[1]}`);
  }
}

/* --- résumé links must all agree with the resumeReady flag ---------------- */
const pdf = mod.PROFILE.resumeFile;
const pdfExists = fs.existsSync(path.join(__dirname, '..', pdf));
if (mod.PROFILE.resumeReady && !pdfExists) fail(`resumeReady is true but ${pdf} is missing`);
for (const [name, out] of Object.entries(rendered)) {
  if (out.includes(pdf) && !mod.PROFILE.resumeReady) fail(`${name}: links to ${pdf} while resumeReady is false`);
}

/* --- community résumé fallback must exist and be selectable --------------- */
const communityPage = path.join(__dirname, '..', 'community-resume.html');
if (!fs.existsSync(communityPage)) fail('community-resume.html is missing');
else {
  const communityHtml = fs.readFileSync(communityPage, 'utf8');
  if (!/<title>[^<]*Community Management Résumé/i.test(communityHtml))
    fail('community-resume.html is missing its descriptive title');
  if (!/window\.print\(\)/.test(communityHtml))
    fail('community-resume.html must provide a Print / Save as PDF action');
  if (!/name="viewport"/.test(communityHtml))
    fail('community-resume.html must be responsive on mobile');
  if (!communityHtml.includes('href="/#/resume"') || communityHtml.includes('href="index.html#/resume"'))
    fail('community-resume.html must link back to the canonical résumé selector route');
}
const bindStart = html.indexOf('function bind(path){');
const bootStart = html.indexOf('/* ======================  6. BOOT');
const bindSource = html.slice(bindStart, bootStart);
const documentKeydownCount = html.split("document.addEventListener('keydown'").length - 1;
const desktopBreakpointCount = html.split("const desktopBreakpoint = window.matchMedia('(min-width:981px)'").length - 1;
if (documentKeydownCount !== 1)
  fail('Mobile Escape handling must use one global document keydown listener');
if (desktopBreakpointCount !== 1)
  fail('Mobile menu desktop-breakpoint handling must use one global media-query listener');
if (bindSource.includes("document.addEventListener('keydown'") || bindSource.includes("window.matchMedia('(min-width:981px)'"))
  fail('bind() must not register global listeners on every route render');
if (!bindSource.includes('closeCurrentMobileSheet = (returnFocus = false)'))
  fail('bind() must refresh the current mobile-menu close handler on every route render');
const renderFunctionIndex = html.indexOf('function render(){');
const bindFunctionIndex = html.indexOf('function bind(path){');
const renderSource = html.slice(renderFunctionIndex, bindFunctionIndex);
if (!renderSource.includes('closeCurrentMobileSheet?.(false);'))
  fail('render() must close the prior mobile sheet before replacing route DOM');
if (!bindSource.includes('let sheetHideTimer = null;') ||
    !bindSource.includes('clearTimeout(sheetHideTimer)') ||
    !bindSource.includes('sheetHideTimer = setTimeout'))
  fail('Mobile menu close animation must cancel a pending hide timer before reopening');
if (!bindSource.includes('app.inert = open;'))
  fail('Mobile navigation must make the obscured page inert while the overlay is open');
if (!bindSource.includes("document.body.style.overflow = open ? 'hidden' : '';"))
  fail('Mobile navigation must continue to lock background scrolling while open');
if (!rendered.Resume || !rendered.Resume.includes('community-resume.html'))
  fail('Résumé page must link to the Community Management web résumé');

/* --- cross-file factual and résumé consistency --------------------------- */
if (!html.includes("degree:'B.Sc.Ed — Mathematics and Education'") ||
    !html.includes("school:'University of Lagos'") ||
    !html.includes("classification:'Second Class Upper'"))
  fail('Education must retain the B.Sc.Ed. qualification, University of Lagos, and Second Class Upper');
const pmEducationSource = fs.readFileSync(path.join(__dirname, 'build-pm-resume.py'), 'utf8');
const cmEducationSource = fs.readFileSync(path.join(__dirname, 'build-community-resume.py'), 'utf8');
const communityEducationSource = fs.readFileSync(communityPage, 'utf8');
const publicEducationSources = [html, pmEducationSource, cmEducationSource, communityEducationSource].join('\n');
if (/CGPA|Completed\s+20\d{2}|3\.8\/5/i.test(publicEducationSources))
  fail('Public education content must not include a CGPA or graduation date');
if (!communityEducationSource.includes('Second Class Upper') ||
    !pmEducationSource.includes('Second Class Upper') ||
    !cmEducationSource.includes('Second Class Upper'))
  fail('Second Class Upper must be retained in both résumé PDF sources and the HTML fallback');
if (!html.includes("name:'Tourist', category:'Travel planning · TS Academy capstone'"))
  fail('Tourist must be described as a travel-planning capstone, not an AI-powered shipped product');
if (!html.includes('itinerary drafts use seeded templates rather than a live AI model'))
  fail('Tourist summary must disclose the current template-based itinerary implementation');
if (html.includes('"alternateName": "Flux"'))
  fail('Person structured data must not publish an unsupported alternate name');
if (!communityHtmlSafe())
  fail('Community résumé must preserve the confirmed Limitless Prop Firm 2022–2023 dates and accurate team attribution');
const communityPdfName = 'Olamide_Olanipekun_Community_Management_Resume.pdf';
if (!fs.existsSync(path.join(__dirname, '..', communityPdfName)))
  fail('Standalone Community Management PDF is missing from the site root');
if (!html.includes("communityResumeFile:'" + communityPdfName + "'") || !html.includes('communityResumeReady:true'))
  fail('Community résumé profile must point to the committed PDF and mark it ready');
if (!html.includes('Download Community Management résumé (PDF)'))
  fail('Résumé page must offer a direct Community Management PDF download');
if (!html.includes('href="community-resume.html"'))
  fail('Print-ready Community HTML fallback must remain available');
if (!html.includes("id:'bdc843d44dc16b9ae29a8349f3010284cab86ea2'"))
  fail('Introduction to Data credential must retain its verified DataCamp identifier');
if (!/linkedin:\s*\{ label:'LinkedIn',\s*value:'Olamide Olanipekun'/.test(html))
  fail('LinkedIn display name must match the portfolio owner name order');
if (html.includes('value:\'Olanipekun Olamide\'')) fail('Stale reversed LinkedIn display name found');
if (html.includes('id="printcv"')) fail('Résumé selector must not offer print-current-page as if it were a résumé download');
if (!/Both résumé versions are available as PDF downloads/.test(html))
  fail('Résumé selector must identify both résumé formats as PDF downloads');
const homeBlock = html.slice(html.indexOf('const Home = () =>'), html.indexOf('const PageHead'));
if (!homeBlock.includes('<a class="tlink" href="#/experience">All projects'))
  fail('Homepage All projects link must route to Experience');
if (!/4\+ years hands-on product\/project management within 7\+ years across product, operations, growth marketing, community management, customer support\/CX, and trading/i.test(html.slice(0, html.indexOf('</head>'))))
  fail('Social description must preserve the approved experience positioning');
function communityHtmlSafe() {
  const page = fs.readFileSync(communityPage, 'utf8');
  return /Product Manager | Growth Lead · YNX<\/h3><span class="date">Apr 2025 – May 2026<\/span>/.test(page)
    && /Built and owned the YNX community from scratch/.test(page)
    && /Sourced moderators to support community moderation, and sourced marketing talent and developers/.test(page)
    && /Product Manager &amp; Growth Operations Lead · Limitless Prop Firm<\/h3><span class="date">Sep 2022 – Dec 2023<\/span>/.test(page)
    && /Community &amp; Customer support specialist · Limitless Prop Firm<\/h3><span class="date">May 2022 – Dec 2023<\/span>/.test(page)
    && /six-person Discord and Telegram team/.test(page)
    && /Community Manager · Gotabit<\/h3><span class="date">Feb 2021 – Oct 2022<\/span>/.test(page)
    && /Community Management &amp; Growth Contributor · Betboom<\/h3><span class="date">Jan 2020 – Sep 2021<\/span>/.test(page)
    && /5–7 minutes/.test(page)
    && /two-person website support team/.test(page)
    && page.includes('At Deserialize, I worked across product and ecosystem operations for a Web3 swap aggregator')
    && !page.includes('building and leading the project’s communities')
    && !page.includes('community presence across Discord, Telegram')
    && !page.includes('<span>Lagos, Nigeria · Remote / Hybrid</span>')
    && (() => {
      const siteOrigin = html.match(/<link rel="canonical" href="(https:\/\/[^/]+)\/">/)?.[1];
      const communityOrigin = page.match(/<link rel="canonical" href="(https:\/\/[^/]+)\/community-resume">/)?.[1];
      return Boolean(siteOrigin && communityOrigin === siteOrigin &&
        page.includes('href="' + siteOrigin + '/#/"') &&
        page.includes('window.print()'));
    })();
}

/* --- dates, role uniqueness, impact attribution, and print safety ----------- */
const expectedExperience = [
  ["YNX", "Apr 2025 – May 2026"],
  ["Dextopus", "Aug 2025 – Feb 2026"],
  ["Debonk Bot", "Jun 2025 – Jan 2026"],
  ["Deserialize", "Apr 2024 – May 2025"],
  ["Limitless Prop Firm", "Sep 2022 – Dec 2023"],
  ["Gotabit", "Feb 2021 – Oct 2022"],
  ["Betboom", "Jan 2020 – Sep 2021"]
];
for (const [org, dates] of expectedExperience) {
  const re = new RegExp("org:'" + escapeRe(org) + "'[\\s\\S]{0,220}?when:'" + escapeRe(dates) + "'");
  if (!re.test(html)) fail(org + " dates must match LinkedIn: " + dates);
}
if (/org:'delabz'/i.test(html)) fail('delabz must not appear in the Experience timeline');
if ((html.match(/org:'Dextopus'/g) || []).length !== 1) fail('Dextopus / Dextopus Bridge must be represented by one Experience entry');
if (!/also:'Community & Customer support specialist · May 2022 – Dec 2023'/.test(html)) fail('Limitless community/support position is missing from Experience timeline');
if (!/const CONCURRENCY = '[^']*Betboom\/Gotabit[^']*Gotabit\/Limitless community support[^']*two Limitless positions[^']*Deserialize\/YNX[^']*YNX\/Debonk Bot[^']*YNX\/Dextopus\/Debonk Bot/.test(html)) fail('Chronology must disclose all supplied overlapping engagements');
if (!/resumeWhen:'May 2022 – Dec 2023'/.test(html)) fail('PM résumé must retain the full May 2022-Dec 2023 Limitless span');
const pmResume = html.slice(html.indexOf('const Resume = () =>'), html.indexOf('const Contact = () =>'));
if (!pmResume.includes('e.resumeWhen || e.when')) fail('PM résumé renderer must use its separate full employer date');
if (/Community & Customer support specialist/.test(pmResume)) fail('PM résumé must exclude the community-only title');
if (/50% reduction in operational bottlenecks/i.test(html)) fail('Stale 50% workflow bottleneck metric remains');
if (!html.includes('30% reduction in workflow bottlenecks at YNX')) fail('Résumé preview must use the current 30% YNX metric');
if (!/Build status: currently paused/.test(html) || !/intermediate retail crypto and forex traders/.test(html)) fail('FortaFlow audience or build status is stale');
if (!/MVP scope: define and confirm crypto\/forex strategy rules/.test(homeBlock)) fail('Homepage FortaFlow teaser must not list later-phase features as MVP');
if (!/Built and owned the YNX community from scratch/.test(html) || !/Sourced moderator talent to support community moderation, and sourced marketing talent and developers/.test(html)) fail('YNX community ownership and talent sourcing must remain visible in Experience');
if (!html.includes("when:'Apr 2025 – May 2026'") || html.includes("when:'Jun 2025 – 2026'"))
  fail('YNX chronology must match the current LinkedIn Apr 2025–May 2026 range');
if (!html.includes("l:'Deserialize swap volume in its first six months'"))
  fail('The $30M metric must be attributed to Deserialize, not an unspecified product');
if (!html.includes("Deserialize, a Web3 swap aggregator, processed over $30M in transaction volume in its first six months (team outcome)."))
  fail('Résumé impact bullet must identify Deserialize as the swap aggregator and preserve team attribution');
const communityPrintCss = communityPage && fs.existsSync(communityPage) ? fs.readFileSync(communityPage, 'utf8') : '';
if (/\.sheet\{[^}]*overflow:hidden/.test(communityPrintCss))
  fail('Community résumé print sheets must not silently clip content');
if (!/\.section,\.job,\.skill\{break-inside:avoid;page-break-inside:avoid\}/.test(communityPrintCss))
  fail('Community résumé print stylesheet must keep sections and jobs together where possible');

/* --- cross-cutting portfolio content and responsive safeguards ----------- */
const processBlock = html.slice(html.indexOf('const PROCESS = ['), html.indexOf('const SKILLS = ['));
if (!processBlock.startsWith('const PROCESS = [') || (processBlock.match(/\{ n:'0[1-7]', h:'/g) || []).length !== 7)
  fail('Product Thinking must define seven numbered stages');
if (!/html\.dataset\.theme|html\[data-theme/.test(html) || !/\.chips\{display:flex;flex-wrap:wrap;gap:7px\}/.test(html))
  fail('Theme and wrapping chip styles must remain present');
if (!/grid-template-columns:minmax\(0,1fr\)/.test(html.slice(html.indexOf('@media (max-width:980px)'), html.indexOf('@media (max-width:720px)'))))
  fail('Main layout must collapse to a single column at tablet/mobile widths');
if (/label:'thinking'[\s\S]{0,250}Seven stages/.test(html) && (processBlock.match(/\{ n:'0[1-7]', h:'/g) || []).length !== 7)
  fail('Thinking page description and stage count disagree');

/* --- referenced local assets must exist ---------------------------------- */
for (const m of html.matchAll(/(?:href|src|content)="((?!https?:|mailto:|#|data:)[\w./-]+\.(?:png|svg|pdf|ico|xml|css|js))"/g)) {
  if (!fs.existsSync(path.join(__dirname, '..', m[1]))) fail(`missing local asset: ${m[1]}`);
}

/* --- share images must be ABSOLUTE, or the card renders blank ------------- */
for (const key of ['og:image', 'og:image:secure_url', 'twitter:image']) {
  const re = new RegExp(`<meta (?:property|name)="${key.replace(/:/g, ':')}" content="([^"]+)"`);
  const m = html.match(re);
  if (!m) { fail(`missing <meta ${key}>`); continue; }
  if (!/^https:\/\//.test(m[1]))
    fail(`${key} must be an absolute https URL (social crawlers will not resolve "${m[1]}")`);
  const local = m[1].split('/').pop();
  if (!fs.existsSync(path.join(__dirname, '..', local)))
    fail(`${key} points at ${local}, which is not in the site root`);
}

/* --- one origin everywhere: canonical, social cards, robots, sitemap,
   standalone résumé, and the maintainer README ----------------------------- */
const root = path.join(__dirname, '..');
const head = html.slice(0, html.indexOf('</head>'));
const canonicalOrigin = head.match(/<link rel="canonical" href="(https:\/\/[^/]+)\/">/)?.[1];
if (!canonicalOrigin) {
  fail('Main page is missing a valid https canonical origin');
} else {
  const metaContent = (key) => {
    const match = head.match(new RegExp('<meta (?:property|name)="' + key + '" content="([^"]+)"'));
    return match?.[1] || '';
  };
  if (metaContent('og:url') !== canonicalOrigin + '/')
    fail('og:url must match the main page canonical origin');
  for (const key of ['og:image', 'og:image:secure_url', 'twitter:image']) {
    const value = metaContent(key);
    if (!value.startsWith(canonicalOrigin + '/'))
      fail(key + ' must use the same origin as the main page canonical');
  }

  const robotsPath = path.join(root, 'robots.txt');
  if (fs.existsSync(robotsPath)) {
    const robots = fs.readFileSync(robotsPath, 'utf8');
    if (!robots.includes('Sitemap: ' + canonicalOrigin + '/sitemap.xml'))
      fail('robots.txt Sitemap directive must use the main page canonical origin');
  }

  const communityPath = path.join(root, 'community-resume.html');
  if (fs.existsSync(communityPath)) {
    const community = fs.readFileSync(communityPath, 'utf8');
    if (!community.includes('<link rel="canonical" href="' + canonicalOrigin + '/community-resume">'))
      fail('Community résumé canonical must use the main page canonical origin');
    if (!community.includes('href="' + canonicalOrigin + '/#/"'))
      fail('Community résumé Portfolio links must use the main page canonical origin');
  }

  const readmePath = path.join(root, 'README.md');
  if (fs.existsSync(readmePath)) {
    const readme = fs.readFileSync(readmePath, 'utf8');
    if (!readme.includes('Live: <' + canonicalOrigin + '/#/>'))
      fail('README live URL must use the main page canonical origin');
    if (!readme.includes('<' + canonicalOrigin + '>'))
      fail('README production URL must use the main page canonical origin');
  }

  console.log('\n  site origin: ' + canonicalOrigin);
}

/* --- sitemap route and lastmod integrity --------------------------------- */
const sitemapPath = path.join(root, 'sitemap.xml');
if (fs.existsSync(sitemapPath)) {
  const sitemap = fs.readFileSync(sitemapPath, 'utf8');
  if (canonicalOrigin && (
      !sitemap.includes('<loc>' + canonicalOrigin + '/</loc>') ||
      !sitemap.includes('<loc>' + canonicalOrigin + '/community-resume</loc>')
    ))
    fail('Sitemap must publish the main page and clean Community résumé URLs on the same canonical origin');
  const lastmods = [...sitemap.matchAll(/<lastmod>(\d{4}-\d{2}-\d{2})<\/lastmod>/g)].map(m => m[1]);
  if (lastmods.length !== 2)
    fail('Sitemap must contain exactly two ISO-format lastmod values');
  else {
    if (lastmods[0] !== lastmods[1])
      fail('Both sitemap URLs must have the same lastmod date');
    for (const date of lastmods) {
      const parsed = new Date(date + 'T00:00:00Z');
      if (!Number.isFinite(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== date)
        fail('Sitemap lastmod must be a valid YYYY-MM-DD date');
      else if (date > new Date().toISOString().slice(0, 10))
        fail('Sitemap lastmod must not be in the future');
    }
  }
}

/* --- domain migration helper must keep all public URLs in sync ------------ */
const setSiteUrlPath = path.join(__dirname, 'set-site-url.sh');
if (fs.existsSync(setSiteUrlPath)) {
  const setSiteUrl = fs.readFileSync(setSiteUrlPath, 'utf8');
  if (!setSiteUrl.includes('community-resume.html') || !setSiteUrl.includes('README.md'))
    fail('set-site-url.sh must update the standalone résumé and maintainer README as well as the main metadata files');
  if (!setSiteUrl.includes('perl -0pi') || !setSiteUrl.includes('OLD_ORIGIN'))
    fail('set-site-url.sh must replace origins literally, not as an unescaped regular expression');
}
/* --- vercel.json must be valid, with only keys Vercel accepts ------------- */
const vjPath = path.join(root, 'vercel.json');
if (fs.existsSync(vjPath)) {
  let vj;
  try { vj = JSON.parse(fs.readFileSync(vjPath, 'utf8')); }
  catch (e) { fail('vercel.json is not valid JSON: ' + e.message); }
  if (vj) {
    for (const h of vj.headers || []) {
      for (const k of Object.keys(h)) {
        if (!['source', 'headers', 'has', 'missing'].includes(k))
          fail(`vercel.json: "${k}" is not a valid key in a headers rule — deploy will be rejected`);
      }
    }
  }
}

/* --- fixed résumé URL, safe CI permissions, and current runner actions ----- */
if (fs.existsSync(vjPath)) {
  const vjPolicy = JSON.parse(fs.readFileSync(vjPath, 'utf8'));
  const pdfRule = (vjPolicy.headers || []).find(h => (h.source || '').endsWith('\\.pdf'));
  const pdfCache = (pdfRule?.headers || []).find(h => (h.key || '').toLowerCase() === 'cache-control')?.value;
  if (pdfCache !== 'public, max-age=0, must-revalidate')
    fail('Product Manager PDF must revalidate; do not cache the fixed résumé URL as immutable');
  const assetRule = (vjPolicy.headers || []).find(h => (h.source || '').includes('svg|png'));
  const assetCache = (assetRule?.headers || []).find(h => (h.key || '').toLowerCase() === 'cache-control')?.value;
  if (assetCache !== 'public, max-age=86400, stale-while-revalidate=604800')
    fail('Stable-named public assets must use bounded caching, not a year-long immutable cache');
  if ((vjPolicy.headers || []).some(h => (h.headers || []).some(x =>
      (x.key || '').toLowerCase() === 'cache-control' && /immutable/i.test(x.value || ''))))
    fail('No stable-named public asset may be cached as immutable');
}
const workflowPath = path.join(root, '.github', 'workflows', 'portfolio-check.yml');
if (fs.existsSync(workflowPath)) {
  const workflow = fs.readFileSync(workflowPath, 'utf8');
  const workflowLines = workflow.split('\n');
  const jobsLine = workflowLines.indexOf('jobs:');
  const validateLine = workflowLines.indexOf('  validate:');
  const publishLine = workflowLines.indexOf('  publish-community-pdf:');
  const topPermissions = jobsLine >= 0 ? workflowLines.slice(0, jobsLine) : [];
  const validateJob = validateLine >= 0 && publishLine > validateLine ? workflowLines.slice(validateLine, publishLine) : [];
  const publishJob = publishLine >= 0 ? workflowLines.slice(publishLine) : [];
  const permissionIs = (lines, value) => lines.some((line, i) =>
    line.trim() === 'permissions:' && lines[i + 1]?.trim() === 'contents: ' + value
  );
  if (!permissionIs(topPermissions, 'read'))
    fail('Workflow-wide permissions must remain read-only');
  if (!validateJob.length || permissionIs(validateJob, 'write') ||
      validateJob.some(line => line.includes('persist-credentials: true') || line.includes('git push')))
    fail('General validation job must not receive a write-capable token or push to the repository');
  if (!publishJob.join('\n').includes("if: github.event_name == 'push' && github.ref == 'refs/heads/main'") ||
      !publishJob.includes('    needs: validate') ||
      !permissionIs(publishJob, 'write') ||
      !publishJob.some(line => line.trim() === 'persist-credentials: true') ||
      !publishJob.some(line => line.includes('git push origin HEAD:main')) ||
      !publishJob.some(line => line.includes('python tools/check-community-resume.py --generated-only')) ||
      !publishJob.some(line => line.includes('python tools/build-pm-resume.py /tmp/product-manager-generated.pdf')) ||
      !publishJob.some(line => line.includes('python tools/check-pm-resume.py --generated-only /tmp/product-manager-generated.pdf')) ||
      !publishJob.some(line => line.includes('git add Olamide-Olanipekun-Product-Manager.pdf Olamide_Olanipekun_Community_Management_Resume.pdf')))
    fail('PDF publishing must be limited to a post-validation job on trusted main pushes, with a regenerated and validated PDF');
  if (!workflow.includes('actions/checkout@v7') || !workflow.includes('actions/setup-node@v7') || !workflow.includes('actions/setup-python@v7'))
    fail('Portfolio validation workflow must use current Node 24-compatible official actions');
}

/* --- the phone number must always route to WhatsApp, never tel: or text ---- */
const wa = mod.SOCIALS && mod.SOCIALS.whatsapp;
if (wa && wa.url) {
  if (!/^https:\/\/wa\.me\/\d{8,15}(\?|$)/.test(wa.url))
    fail(`SOCIALS.whatsapp.url must be a wa.me deep link, got "${wa.url}"`);
  const digits = (wa.value || '').replace(/\D/g, '');
  if (digits && !wa.url.includes(digits))
    fail(`SOCIALS.whatsapp: displayed number ${wa.value} does not match the wa.me link`);
  for (const [name, out] of Object.entries(rendered)) {
    if (/href="tel:/.test(out)) fail(`${name}: tel: link found — the number must open WhatsApp`);
    // every occurrence of the displayed number has to sit inside a wa.me anchor
    for (const m of out.matchAll(new RegExp(escapeRe(wa.value), 'g'))) {
      const open = out.lastIndexOf('<a', m.index);
      const close = out.lastIndexOf('</a>', m.index);
      const inAnchor = open > close;
      const anchor = inAnchor ? out.slice(open, out.indexOf('>', open)) : '';
      if (!inAnchor || !anchor.includes('wa.me'))
        fail(`${name}: "${wa.value}" is rendered outside a wa.me link — clicking it would not open WhatsApp`);
    }
  }
}
function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

console.log('\n' + (fails ? `${fails} problem(s) found.` : 'All checks passed.'));
process.exit(fails ? 1 : 0);
