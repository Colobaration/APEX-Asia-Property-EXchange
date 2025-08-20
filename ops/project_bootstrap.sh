#!/usr/bin/env bash
set -euo pipefail

# Requires: gh CLI authenticated with GH_TOKEN

: "${GH_TOKEN:?GH_TOKEN is required}"
: "${GH_OWNER:?GH_OWNER is required}"
: "${GH_PROJECT_NAME:?GH_PROJECT_NAME is required}"

export GH_TOKEN

# Ensure project exists (Org-level preferred; fallback to user)
project_id=""

if gh project list --owner "$GH_OWNER" --format json | jq -r '.[] | select(.title==env.GH_PROJECT_NAME) | .id' | grep -q .; then
  project_id=$(gh project list --owner "$GH_OWNER" --format json | jq -r \
    '.[] | select(.title==env.GH_PROJECT_NAME) | .id' | head -n1)
else
  project_id=$(gh project create --owner "$GH_OWNER" --title "$GH_PROJECT_NAME" --format json | jq -r '.id')
fi

echo "Project ID: $project_id"

# Create fields (if not exist)
ensure_single_select() {
  local name="$1"; shift
  local options_csv="$1"; shift
  if ! gh project field-list $project_id --format json | jq -r '.fields[]?.name' | grep -Fxq "$name"; then
    gh project field-create $project_id --name "$name" --data-type SINGLE_SELECT \
      --single-select-options "$options_csv" >/dev/null
  fi
}

ensure_text() {
  local name="$1"
  if ! gh project field-list $project_id --format json | jq -r '.fields[]?.name' | grep -Fxq "$name"; then
    gh project field-create $project_id --name "$name" --data-type TEXT >/dev/null
  fi
}

ensure_single_select "Статус" "К выполнению,В работе,На ревью,Готово"
ensure_single_select "Область" "инфра,бэкенд,фронтенд,аналитика,интеграции,документация,QA"
ensure_single_select "Приоритет" "P0,P1,P2"
ensure_text "Ответственный"

# Save project number for later use
project_number=$(gh project view $project_id --format json | jq -r '.number')
mkdir -p ops
echo -n "$project_number" > ops/.project_number
echo "Saved PROJECT_NUMBER=$project_number to ops/.project_number"


