#!/usr/bin/env bash
# Integration test for tools/set-site-url.sh. Uses a temporary fixture only.
set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/tools"
cp "$TOOLS_DIR/set-site-url.sh" "$TMP/tools/set-site-url.sh"

OLD="https://old-origin.example"
NEW="https://new-origin.example"

cat > "$TMP/index.html" <<EOF
<!doctype html>
<link rel="canonical" href="$OLD/">
<meta property="og:url" content="$OLD/">
<meta property="og:image" content="$OLD/og-image.png">
<meta name="twitter:image" content="$OLD/twitter-card.png">
EOF

cat > "$TMP/community-resume.html" <<EOF
<!doctype html>
<link rel="canonical" href="$OLD/community-resume">
<a href="$OLD/#/">Portfolio</a>
<a href="$OLD/#/">Portfolio</a>
EOF

cat > "$TMP/robots.txt" <<EOF
User-agent: *
Allow: /
Sitemap: $OLD/sitemap.xml
EOF

cat > "$TMP/sitemap.xml" <<EOF
<urlset>
  <url><loc>$OLD/</loc><lastmod>2026-11-10</lastmod></url>
  <url><loc>$OLD/community-resume</loc><lastmod>2026-11-10</lastmod></url>
</urlset>
EOF

cat > "$TMP/README.md" <<EOF
Live: <$OLD/#/> · Repo: https://github.com/example/repo
Production: <$OLD>
EOF

bash "$TMP/tools/set-site-url.sh" "$NEW" >/dev/null

for file in index.html community-resume.html robots.txt sitemap.xml README.md; do
  if grep -Fq "$OLD" "$TMP/$file"; then
    echo "FAIL: stale origin remains in $file" >&2
    exit 1
  fi
  if ! grep -Fq "$NEW" "$TMP/$file"; then
    echo "FAIL: new origin missing from $file" >&2
    exit 1
  fi
done

mapfile -t lastmods < <(grep -oE '<lastmod>[0-9]{4}-[0-9]{2}-[0-9]{2}</lastmod>' "$TMP/sitemap.xml")
TODAY="<lastmod>$(date -u +%F)</lastmod>"
if [[ "${#lastmods[@]}" -ne 2 || "${lastmods[0]}" != "$TODAY" || "${lastmods[1]}" != "$TODAY" ]]; then
  echo "FAIL: sitemap lastmod values were not updated consistently" >&2
  exit 1
fi

before="$(sha256sum "$TMP/index.html" "$TMP/community-resume.html" "$TMP/robots.txt" "$TMP/sitemap.xml" "$TMP/README.md" | sha256sum)"
bash "$TMP/tools/set-site-url.sh" "$NEW" >/dev/null
after="$(sha256sum "$TMP/index.html" "$TMP/community-resume.html" "$TMP/robots.txt" "$TMP/sitemap.xml" "$TMP/README.md" | sha256sum)"
if [[ "$before" != "$after" ]]; then
  echo "FAIL: repeating the same origin migration changed files" >&2
  exit 1
fi

echo "Site URL migration fixture passed (all files updated; rerun is idempotent)."
