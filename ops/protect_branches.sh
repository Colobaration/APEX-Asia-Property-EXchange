#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?GH_TOKEN is required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"

protect() {
  local branch="$1"
  gh api -X PUT \
    -H "Accept: application/vnd.github+json" \
    "/repos/${GITHUB_REPOSITORY}/branches/${branch}/protection" \
    -f required_pull_request_reviews='{"required_approving_review_count":1,"require_code_owner_reviews":true}' \
    -f enforce_admins=true \
    -f restrictions='null' \
    -f required_status_checks='{"strict":false,"contexts":[]}' \
    -f allow_deletions=false \
    -f allow_force_pushes=false >/dev/null
  echo "Protected ${branch}"
}

protect main || true
protect dev || true


