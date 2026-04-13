#!/usr/bin/env bash
#
# kill-switch.sh — toggle the coarse.ink submission kill switch.
#
# Flips the `system_status.accepting_reviews` row in Supabase so the
# landing-page banner fires and /api/submit (and /api/presign) start
# returning 503. Use when you need to pull the site offline quickly
# while fixing something without tearing the Vercel deployment down.
#
# Usage:
#   scripts/kill-switch.sh pause [message]   # stop accepting submissions
#   scripts/kill-switch.sh resume            # resume accepting submissions
#   scripts/kill-switch.sh status            # show current state
#
# If [message] is omitted on pause, uses a default "temporarily down"
# banner. Reads Supabase URL + service key from web/.env.local — no
# other configuration required. Safe to run from anywhere in the repo.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/web/.env.local"

DEFAULT_MESSAGE="coarse.ink is temporarily down — we'll be back soon."

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: $ENV_FILE not found." >&2
  echo "This script reads NEXT_PUBLIC_SUPABASE_URL + SUPABASE_SERVICE_KEY from web/.env.local." >&2
  exit 1
fi

SUPABASE_URL="$(grep -E '^NEXT_PUBLIC_SUPABASE_URL=' "$ENV_FILE" | cut -d= -f2- | tr -d '"' | tr -d "'")"
SUPABASE_KEY="$(grep -E '^SUPABASE_SERVICE_KEY=' "$ENV_FILE" | cut -d= -f2- | tr -d '"' | tr -d "'")"

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_KEY:-}" ]; then
  echo "Error: NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_KEY missing from $ENV_FILE" >&2
  exit 1
fi

SUBCOMMAND="${1:-status}"
if [ "$#" -gt 0 ]; then shift; fi
MESSAGE="${*:-}"

api_patch() {
  curl --fail --silent --show-error \
    -X PATCH "$SUPABASE_URL/rest/v1/system_status?id=eq.1" \
    -H "apikey: $SUPABASE_KEY" \
    -H "Authorization: Bearer $SUPABASE_KEY" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=representation" \
    -d "$1"
}

api_get() {
  curl --fail --silent --show-error \
    "$SUPABASE_URL/rest/v1/system_status?select=accepting_reviews,banner_message,updated_at&id=eq.1" \
    -H "apikey: $SUPABASE_KEY" \
    -H "Authorization: Bearer $SUPABASE_KEY"
}

json_escape() {
  # Minimal JSON string escape for the banner message. Handles backslash,
  # double-quote, newline, carriage return, tab. Doesn't cover every
  # edge case a JSON serializer would, but operator-typed banners are
  # boring strings in practice.
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

case "$SUBCOMMAND" in
  pause)
    MSG="${MESSAGE:-$DEFAULT_MESSAGE}"
    escaped_msg="$(json_escape "$MSG")"
    body="{\"accepting_reviews\":false,\"banner_message\":\"$escaped_msg\"}"
    api_patch "$body" > /dev/null
    echo "PAUSED — coarse.ink is no longer accepting submissions."
    echo "Banner: $MSG"
    echo
    echo "Resume with: scripts/kill-switch.sh resume  (or: make resume)"
    ;;
  resume)
    api_patch '{"accepting_reviews":true,"banner_message":null}' > /dev/null
    echo "RESUMED — coarse.ink is accepting submissions again."
    ;;
  status)
    response="$(api_get)"
    if command -v jq >/dev/null 2>&1; then
      accepting="$(printf '%s' "$response" | jq -r '.[0].accepting_reviews')"
      banner="$(printf '%s' "$response" | jq -r '.[0].banner_message // "(none)"')"
      updated="$(printf '%s' "$response" | jq -r '.[0].updated_at')"
      if [ "$accepting" = "true" ]; then
        echo "State:  ACCEPTING submissions"
      else
        echo "State:  PAUSED"
      fi
      echo "Banner: $banner"
      echo "Since:  $updated"
    else
      echo "$response"
      echo
      echo "(install jq for a prettier status output)"
    fi
    ;;
  *)
    echo "Usage: $0 {pause [message]|resume|status}" >&2
    exit 1
    ;;
esac
