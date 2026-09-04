#!/usr/bin/env bash
#
# One-shot: verify -> git repo -> push to GitHub -> Vercel -> fix the URL.
#
#   bash deploy.sh
#
# Safe to re-run. On a second run it skips whatever already exists and just
# pushes, which is also how you ship an edit later.
#
# Needs: git and node. The GitHub repo already exists, so the GitHub CLI (gh) is
# no longer required — it is only used, if it happens to be installed, to save
# you from typing a credential. Vercel is optional too — if the `vercel` CLI is
# missing the script stops after the push and prints the three clicks that
# finish the job from the dashboard instead.

set -uo pipefail
cd "$(dirname "$0")"

# The GitHub repo this site is pushed to. It already exists, so nothing here ever
# creates one — change this one line (or export REPO_URL) to aim somewhere else.
REPO_URL="${REPO_URL:-https://github.com/Flux-web3/Portfolio.git}"
REPO_NAME="$(basename "$REPO_URL" .git)"   # 'Portfolio' — only used in the messages below
say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()  { printf '\n\033[31mstopped:\033[0m %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- 1. verify --
say "1/5  Checking the site before anything is published"
command -v node >/dev/null || die "node is not installed — https://nodejs.org"
node tools/check.js || die "tools/check.js found problems. Fix them before deploying."

# ------------------------------------------------------------------- 2. git --
say "2/5  Local git repository"
command -v git >/dev/null || die "git is not installed — https://git-scm.com/downloads"

if [[ -d .git ]]; then
  # A .git can arrive half-built — this project was assembled on a filesystem
  # that refused unlink(), so an empty repo with a stale lockfile may be sitting
  # here. Clear the locks, and re-init if there is no commit to build on.
  find .git -name '*.lock' -maxdepth 2 -delete 2>/dev/null || true
  if git rev-parse --git-dir >/dev/null 2>&1 && git rev-parse HEAD >/dev/null 2>&1; then
    ok "already a git repo"
  else
    rm -rf .git || die "could not remove the incomplete .git — delete that folder by hand and re-run"
    git init -q -b main
    ok "replaced an incomplete .git and initialised on branch main"
  fi
else
  git init -q -b main
  ok "initialised on branch main"
fi

git config user.name  >/dev/null 2>&1 || git config user.name  "Olanipekun Olamide"
git config user.email >/dev/null 2>&1 || git config user.email "flux.fx05@gmail.com"

git add -A
if git diff --cached --quiet 2>/dev/null && git rev-parse HEAD >/dev/null 2>&1; then
  ok "nothing new to commit"
else
  git commit -q -m "Portfolio: Product Manager and product builder site" \
                 -m "Single-file static site, no build step. Hash routing across eight pages, dark/light themes, reduced-motion support, JSON-LD, and a print stylesheet for the resume page."
  ok "committed"
fi

# ---------------------------------------------------------------- 3. GitHub --
say "3/5  GitHub"

# git's own words for a refused credential are famously unhelpful, and this is the
# step most likely to stop a first run dead, so every call that touches the network
# reports through here and says what to actually do about it.
git_or_die() {                       # git_or_die <what went wrong> <git args...>
  local what="$1"; shift
  local out
  out="$(git "$@" 2>&1)" && return 0
  [[ -n "$out" ]] && sed 's/^/      /' <<<"$out" >&2
  if [[ "$REMOTE_URL" == *github.com* ]] &&
     grep -qiE 'authenticat|could not read (username|password)|terminal prompts disabled|permission denied|403|access rights|invalid username' <<<"$out"; then
    warn "GitHub would not let us in. Any one of these fixes it:"
    echo  "      * install https://cli.github.com, then:  gh auth login"
    echo  "      * or paste a token instead of a password at the HTTPS prompt —"
    echo  "        github.com/settings/tokens, classic, 'repo' scope — and keep it:"
    echo  "            git config --global credential.helper store"
    echo  "      * or move this remote to SSH, if your key is already on GitHub:"
    echo  "            git remote set-url origin $SSH_URL"
    die   "then re-run this script"
  fi
  die "$what — git's output above says why"
}

# gh is no longer needed to make the repo, because the repo already exists. But if
# it is installed it is the least painful way to get a credential onto the machine,
# so let it log in before git has to ask.
if command -v gh >/dev/null && ! gh auth status >/dev/null 2>&1; then
  gh auth login || warn "gh login skipped — git will ask for a credential instead"
fi

CURRENT="$(git remote get-url origin 2>/dev/null)"
if [[ -z "$CURRENT" ]]; then
  git remote add origin "$REPO_URL" || die "could not add the remote 'origin'"
  ok "remote 'origin' -> $REPO_URL"
elif [[ "${CURRENT%.git}" == "${REPO_URL%.git}" ]]; then
  ok "remote 'origin' already points at $REPO_URL"
else
  # A different URL here is far likelier to be deliberate — an SSH remote for the
  # same repo, a fork, a mirror — than a mistake, and silently overwriting it could
  # push this site into somebody else's repo. Show both and let the user say.
  warn "remote 'origin' is not the URL in REPO_URL:"
  echo  "      origin now  $CURRENT"
  echo  "      REPO_URL    $REPO_URL"
  read -r -p "  Repoint 'origin' at REPO_URL? [y/N] " reply
  if [[ "$reply" =~ ^[Yy] ]]; then
    git remote set-url origin "$REPO_URL" || die "could not repoint 'origin'"
    ok "repointed to $REPO_URL"
  else
    ok "left alone — pushing to $CURRENT instead"
  fi
fi
REMOTE_URL="$(git remote get-url origin)"
SSH_URL="${REMOTE_URL/https:\/\/github.com\//git@github.com:}"

# Look before pushing. A repo created through the GitHub UI usually arrives with a
# commit already on it — the "Add a README" tickbox, a .gitignore, a licence — and
# that commit shares no ancestor with this history, so a plain push is rejected
# with "Updates were rejected because the remote contains work that you do not
# have locally". Finding it out here means we can offer a way through it.
# --prune as well, so a remote-tracking branch left behind by a previous origin
# URL cannot answer for this one.
git_or_die "could not reach $REMOTE_URL" fetch -q --prune origin

BRANCH="$(git symbolic-ref --quiet --short HEAD || echo main)"

# Which branch is the remote's default? GitHub has handed out 'main' for years, but
# a repo made from an older template can still be on 'master', so ask rather than
# assume. An empty repo has not decided yet, and then whatever git init gave us
# becomes the default — that is 'main'.
git remote set-head origin --auto >/dev/null 2>&1 || true
TARGET="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD || true)"
TARGET="${TARGET#origin/}"
[[ -n "$TARGET" ]] || TARGET="$BRANCH"

FORCE=0
if ! git rev-parse --quiet --verify "refs/remotes/origin/$TARGET" >/dev/null; then
  ok "the remote has no '$TARGET' branch yet — this push creates it"
elif git merge-base --is-ancestor "refs/remotes/origin/$TARGET" HEAD; then
  ok "remote '$TARGET' is already an ancestor of this history — a plain push lands"
else
  warn "the remote's '$TARGET' holds work that is not in this history:"
  git --no-pager log --oneline --max-count=5 "refs/remotes/origin/$TARGET" | sed 's/^/      /'
  echo  "      files there: $(git --no-pager ls-tree -r --name-only "refs/remotes/origin/$TARGET" | head -10 | tr '\n' ' ')"
  echo
  echo  "  A plain push would be rejected. Three ways on:"
  echo  "      1  replace  put this history over it (git push --force-with-lease);"
  echo  "                  the commits listed above are thrown away"
  echo  "      2  merge    replay this history on top of it first, then push"
  echo  "                  (git pull --rebase --allow-unrelated-histories)"
  echo  "      3  abort    change nothing"
  echo
  # 2 is the default because it throws nothing away: if what is up there turns out
  # to be more than a placeholder, it survives. 1 is there because for a repo the
  # user created minutes ago a placeholder is almost certainly all it is — but it
  # only ever runs when it is typed, and --force-with-lease still refuses if the
  # remote moved since the fetch above.
  read -r -p "  1, 2 or 3? [2] " reply
  case "${reply:-2}" in
    1) FORCE=1
       warn "replacing the remote's '$TARGET' with this history" ;;
    3) die "nothing pushed. 'origin' is set, so plain 'git push' is yours to run once you decide." ;;
    *) # --allow-unrelated-histories because the two roots are unrelated by
       # construction. A conflict is likely — GitHub's placeholder README.md has
       # the same name as this one — and on failure the rebase is unwound rather
       # than left half-finished, which would leave a tree full of conflict markers
       # that a re-run of this script would cheerfully commit and push.
       if out="$(git pull --rebase --allow-unrelated-histories origin "$TARGET" 2>&1)"; then
         ok "replayed this history on top of the remote's '$TARGET'"
       else
         sed 's/^/      /' <<<"$out" >&2
         git rebase --abort >/dev/null 2>&1 || true
         warn "the rebase could not finish, so it was rolled back — nothing changed."
         echo  "      Either settle it by hand:"
         echo  "          git pull --rebase --allow-unrelated-histories origin $TARGET"
         echo  "          # fix the files it names, git add them, git rebase --continue"
         echo  "          git push -u origin $BRANCH:$TARGET"
         echo  "      or, if the remote only holds GitHub's placeholder, re-run this"
         echo  "      script and choose 1."
         die   "rebase stopped on a conflict"
       fi ;;
  esac
fi

# Pushing to a public repo is deliberate. Everything in it — email, links, the
# résumé — is already published on the website itself, so a private repo would
# protect nothing. There is no .env, key, or token here; tools/check.js and the
# pre-push review confirmed that.
if [[ "$FORCE" == 1 ]]; then
  git_or_die "push to $REMOTE_URL failed" push -q --force-with-lease -u origin "$BRANCH:$TARGET"
else
  git_or_die "push to $REMOTE_URL failed" push -q -u origin "$BRANCH:$TARGET"
fi
ok "pushed '$BRANCH' to $REMOTE_URL ('$TARGET')"

# ---------------------------------------------------------------- 4. Vercel --
say "4/5  Vercel"
if ! command -v vercel >/dev/null; then
  warn "the Vercel CLI is not installed. Either:"
  echo  "      npm i -g vercel   &&   bash deploy.sh"
  echo  "    or import the repo from the dashboard, which needs no CLI:"
  echo  "      1. https://vercel.com/new"
  echo  "      2. pick the '$REPO_NAME' repo you just pushed"
  echo  "      3. Framework Preset: Other. Leave build & output settings empty. Deploy."
  echo
  warn "then finish with step 5 below."
  DEPLOY_URL=""
else
  vercel link --yes >/dev/null 2>&1 || true
  DEPLOY_URL="$(vercel deploy --prod --yes 2>/dev/null | tail -1)"
  [[ "$DEPLOY_URL" == https://* ]] && ok "live at $DEPLOY_URL" || warn "could not read the deploy URL from the CLI output"
fi

# ------------------------------------------------------------------- 5. URL --
say "5/5  Point the canonical URL, share image and sitemap at the real domain"
cat <<'NOTE'
  index.html, robots.txt and sitemap.xml currently carry a PLACEHOLDER origin.
  Until it matches the live domain, Google is told the real page lives at a URL
  that does not exist, and LinkedIn/X/Facebook cannot fetch the share image.
NOTE

if [[ -n "${DEPLOY_URL:-}" ]]; then
  ORIGIN="$(printf '%s' "$DEPLOY_URL" | sed -E 's#(https://[^/]+).*#\1#')"
  echo
  read -r -p "  Set the origin to $ORIGIN now? [Y/n] " reply
  if [[ ! "$reply" =~ ^[Nn] ]]; then
    bash tools/set-site-url.sh "$ORIGIN" \
      && git commit -qam "Point canonical, og:image and sitemap at the live domain" \
      && git push -q \
      && ok "origin updated and redeployed by the git push"
  fi
else
  echo
  echo "  Once you know the domain, run:"
  echo "      bash tools/set-site-url.sh https://your-real-domain"
  echo "      git commit -am 'Point canonical and sitemap at the live domain' && git push"
fi

say "Done."
echo "  Re-scrape the share card so the platforms drop any cached copy:"
echo "    LinkedIn  https://www.linkedin.com/post-inspector/"
echo "    Facebook  https://developers.facebook.com/tools/debug/"
