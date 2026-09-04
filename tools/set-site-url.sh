#!/usr/bin/env bash
# Rewrites the site's origin everywhere it appears: the canonical link, og:url,
# og:image, twitter:image, robots.txt's Sitemap line, and sitemap.xml's <loc>.
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
OLD="$(grep -oP '(?<=<link rel="canonical" href=")https://[^/"]+' index.html | head -1)"
[[ -n "$OLD" ]] || { echo "error: could not read the current origin from index.html" >&2; exit 1; }

if [[ "$OLD" == "$NEW" ]]; then
  echo "Already set to $NEW — nothing to do."
  exit 0
fi

for f in index.html robots.txt sitemap.xml; do
  [[ -f "$f" ]] || continue
  before="$(grep -c -- "$OLD" "$f" || true)"
  # Bare origin, not a regex: sed's delimiter is | because the URL contains /.
  sed -i "s|${OLD}|${NEW}|g" "$f"
  echo "  $f — ${before} occurrence(s) updated"
done

# sitemap lastmod should reflect the deploy, not the day the file was written.
sed -i "s|<lastmod>[0-9-]*</lastmod>|<lastmod>$(date -u +%F)</lastmod>|" sitemap.xml

echo
echo "Origin changed:  $OLD  ->  $NEW"
echo "Now commit and push:"
echo "  git commit -am 'Point canonical, og:image and sitemap at the live domain' && git push"
echo
echo "Then re-scrape the share card so the platforms drop their cached copy:"
echo "  LinkedIn  https://www.linkedin.com/post-inspector/"
echo "  Facebook  https://developers.facebook.com/tools/debug/"
echo "  X         https://cards-dev.twitter.com/validator"
