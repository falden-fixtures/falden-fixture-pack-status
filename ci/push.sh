#!/bin/bash
# The publish job's last step (REG-416): run the publish command on top of main as it stands, commit what it wrote
# with the job's own GITHUB_TOKEN, and push it to main. A push refused because main moved is tried again on top of
# the new main, three tries in all. The token reaches git through its environment, never an argument or a file, and
# is masked in the log.
#   ci/push.sh <commit message> <publish command...>
set -euo pipefail
: "${GITHUB_TOKEN:?the job's token is not set}"
message="$1"; shift
auth=$(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 | tr -d '\n')
echo "::add-mask::$auth"
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $auth"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
for try in 1 2 3; do
  git fetch -q origin main
  git reset -q --hard FETCH_HEAD
  env -u GITHUB_TOKEN -u GIT_CONFIG_COUNT -u GIT_CONFIG_KEY_0 -u GIT_CONFIG_VALUE_0 "$@"
  git add -A records README.md
  if git diff --cached --quiet; then
    echo "publish: nothing new to record"
    exit 0
  fi
  git commit -q -m "$message"
  if git push -q origin HEAD:main; then
    echo "publish: recorded and pushed, try $try"
    exit 0
  fi
  echo "publish: main moved; trying again on top of it ($try of 3)"
  sleep $(( try * 5 ))
done
exit 1
