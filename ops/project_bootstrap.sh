#!/usr/bin/env bash
set -euo pipefail

# Requires: gh CLI authenticated with GH_TOKEN

: "${GH_TOKEN:?GH_TOKEN is required}"
: "${GH_OWNER:?GH_OWNER is required}"
: "${GH_PROJECT_NAME:?GH_PROJECT_NAME is required}"

export GH_TOKEN

# Ensure project exists (org or user). Work with project NUMBER explicitly
project_number=""

projects_json=$(gh project list --owner "$GH_OWNER" --format json)
# Support both shapes: array or {projects:[...]}. Be defensive about element shapes.
project_number=$(echo "$projects_json" | jq -r --arg T "$GH_PROJECT_NAME" '
  (
    if type=="array" then .
    elif (.projects? | type)=="array" then .projects
    else [] end
  )
  | map(select((.title // empty)==$T))
  | (first // {})
  | (.number // empty)
')

if [ -z "$project_number" ] || [ "$project_number" = "null" ]; then
  project_number=$(gh project create --owner "$GH_OWNER" --title "$GH_PROJECT_NAME" --format json | jq -r '.number')
fi

echo "Project NUMBER: $project_number"

# Create fields (if not exist)
ensure_single_select() {
  local name="$1"; shift
  local options_csv="$1"; shift
  if ! gh project field-list "$project_number" --owner "$GH_OWNER" --format json | jq -r 'if type=="array" then . else .fields end | .[]? | .name' | grep -Fxq "$name"; then
    gh project field-create "$project_number" --owner "$GH_OWNER" --name "$name" --data-type SINGLE_SELECT \
      --single-select-options "$options_csv" >/dev/null
  fi
}

ensure_text() {
  local name="$1"
  if ! gh project field-list "$project_number" --owner "$GH_OWNER" --format json | jq -r 'if type=="array" then . else .fields end | .[]? | .name' | grep -Fxq "$name"; then
    gh project field-create "$project_number" --owner "$GH_OWNER" --name "$name" --data-type TEXT >/dev/null
  fi
}

ensure_single_select "Статус" "К выполнению,В работе,На ревью,Готово"
ensure_single_select "Область" "инфра,бэкенд,фронтенд,аналитика,интеграции,документация,QA"
ensure_single_select "Приоритет" "P0,P1,P2"
ensure_text "Ответственный"

mkdir -p ops
echo -n "$project_number" > ops/.project_number
echo "Saved PROJECT_NUMBER=$project_number to ops/.project_number"


