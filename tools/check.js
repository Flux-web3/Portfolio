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

/* --- one origin everywhere: canonical, og:url, images, robots, sitemap ---- */
const root = path.join(__dirname, '..');
const origins = new Set();
const collect = (text) => {
  for (const m of text.matchAll(/https:\/\/[^"'\s<>]+/g)) {
    const o = m[0].match(/^https:\/\/[^/]+/)[0];
    // third-party origins are expected; only the site's own must agree
    if (/vercel\.app|olamide|olanipekun/i.test(o)) origins.add(o);
  }
};
collect(html);
for (const f of ['robots.txt', 'sitemap.xml']) {
  if (fs.existsSync(path.join(root, f))) collect(fs.readFileSync(path.join(root, f), 'utf8'));
}
if (origins.size > 1)
  fail(`site origin disagrees across files: ${[...origins].join(' vs ')} — run tools/set-site-url.sh`);
else if (origins.size === 1)
  console.log(`\n  site origin: ${[...origins][0]}`);

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
