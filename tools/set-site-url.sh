#!/usr/bin/env bash
# Reconciles the site's public origin everywhere it appears: main-page metadata,
# the standalone community résumé and its portfolio links, robots.txt, sitemap.xml,
# and the maintainer README. Literal replacement avoids treating domain dots as regex.
#
# Run this once, right after the first Vercel deploy tells you the real domain:
#   bash tools/set-site-url.sh https://olamide.vercel.app
#
# Idempotent — safe to run again if you later move to a custom domain.
set -euo pipefail

NEW="${1:-}"
if [[ -z "$NEW" ]]; then
  echo "usage: bash tools/set-site-url.sh https://your-domain.com" >&2
  exit 64
fi
[[ "$NEW" =~ ^https://[^/[:space:]]+$ ]] || {
  echo "error: pass an https origin with no trailing slash and no path, e.g. https://olamide.vercel.app" >&2
  exit 64
}

cd "$(dirname "$0")/.."

# Whatever origin is in the canonical tag right now is the one to replace.
OLD="$(sed -nE 's#.*<link rel="canonical" href="(https://[^"/]+)".*#\1#p' index.html | head -1)"
[[ -n "$OLD" ]] || { echo "error: could not read the current origin from index.html" >&2; exit 1; }

if [[ "$OLD" == "$NEW" ]]; then
  echo "Main canonical is already $NEW — reconciling every public reference."
fi

for f in index.html community-resume.html robots.txt sitemap.xml README.md; do
  [[ -f "$f" ]] || continue
  before="$(grep -F -o -- "$OLD" "$f" | wc -l | tr -d '[:space:]' || true)"
  OLD_ORIGIN="$OLD" NEW_ORIGIN="$NEW" perl -0pi -e 's/\Q$ENV{OLD_ORIGIN}\E/$ENV{NEW_ORIGIN}/g' "$f"
  echo "  $f — ${before:-0} occurrence(s) reconciled"
done

# Sitemap lastmod reflects an actual origin migration, not an idempotent re-run.
if [[ "$OLD" != "$NEW" ]]; then
  LASTMOD="$(date -u +%F)"
  LASTMOD="$LASTMOD" perl -pi -e 's#<lastmod>[0-9-]*</lastmod>#<lastmod>$ENV{LASTMOD}</lastmod>#g' sitemap.xml
fi

echo
echo "Origin changed:  $OLD  ->  $NEW"
echo "Now commit and push:"
echo "  git commit -am 'Point canonical, og:image and sitemap at the live domain' && git push"
echo
echo "Then re-scrape the share card so the platforms drop their cached copy:"
echo "  LinkedIn  https://www.linkedin.com/post-inspector/"
echo "  Facebook  https://developers.facebook.com/tools/debug/"
echo "  X         https://cards-dev.twitter.com/validator"
