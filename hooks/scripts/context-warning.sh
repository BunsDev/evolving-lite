#!/bin/bash
# Context Warning - PreToolUse hook (Evolving Lite)
# Adapted from Evolving v6.1. Simplified: no DSV Pulse, no rate tracking.
#
# Strategy:
# - 70%: warn (summary-only mode)
# - 93%: auto-handoff trigger
# - Below 50% after compaction: reset handoff flag
# - Bash 3 compatible (no associative arrays)

session_id="${CLAUDE_SESSION_ID:-$PPID}"
pct_file="/tmp/claude-context-pct-${session_id}.txt"
last_warn_file="/tmp/evolving-lite-ctx-warn-${session_id}.txt"
handoff_triggered_file="/tmp/evolving-lite-handoff-${session_id}.txt"

# Thresholds (hardcoded for simplicity - no jq dependency)
THRESH_WARN=70
THRESH_AUTO=93
THRESH_RESET=50
DEBOUNCE_SECONDS=120

now=$(date +%s)
last_warn=0
if [ -f "$last_warn_file" ]; then
  last_warn=$(cat "$last_warn_file" 2>/dev/null || echo 0)
  # Sanitize
  last_warn=$(echo "$last_warn" | tr -cd '0-9')
  [ -z "$last_warn" ] && last_warn=0
fi
time_since=$((now - last_warn))

# Read context percentage from Claude Code's tmp file
pct=0
if [ -f "$pct_file" ]; then
  pct=$(cat "$pct_file" 2>/dev/null || echo 0)
  pct=$(echo "$pct" | tr -cd '0-9')
  [ -z "$pct" ] && pct=0
fi

# Reset handoff flag after compaction
if [ "$pct" -lt "$THRESH_RESET" ] && [ -f "$handoff_triggered_file" ]; then
  rm -f "$handoff_triggered_file"
fi

# Below warn threshold: quick exit
if [ "$pct" -lt "$THRESH_WARN" ]; then
  echo '{}'
  exit 0
fi

# Debounce (skip if at auto-handoff level)
if [ "$pct" -lt "$THRESH_AUTO" ] && [ "$time_since" -lt "$DEBOUNCE_SECONDS" ]; then
  echo '{}'
  exit 0
fi

# Record warning time
echo "$now" > "$last_warn_file"

if [ "$pct" -ge "$THRESH_AUTO" ]; then
  # Auto-handoff: suggest creating a handoff document
  if [ ! -f "$handoff_triggered_file" ]; then
    echo "$now" > "$handoff_triggered_file"
    echo "{\"systemMessage\": \"AUTO-HANDOFF: Context at ${pct}%. Create a handoff document with /whats-next, then continue working. After compaction, context resets and you can keep going.\", \"continue\": true}"
    exit 0
  fi
  # Already triggered, just warn
  echo "{\"systemMessage\": \"Context at ${pct}%. Handoff already created. Compaction will happen automatically.\", \"continue\": true}"
  exit 0
elif [ "$pct" -ge "$THRESH_WARN" ]; then
  # Warning: summary-only mode
  echo "{\"systemMessage\": \"Context at ${pct}%. Summary-only mode: avoid loading large files. At ${THRESH_AUTO}% a handoff will be auto-created.\", \"continue\": true}"
  exit 0
fi

echo '{}'
exit 0
