#!/usr/bin/env bash
# Extract a behavioral snapshot of a Cobra CLI.
# Runs INSIDE the Docker container (mount this script as a volume).
#
# Usage:
#   docker run --rm --network none \
#     -v "$PWD/scripts:/scripts:ro" \
#     steampipe:test bash /scripts/extract-cli-snapshot.sh
#
# Override binary:  CLI_BIN=steampipe bash /scripts/extract-cli-snapshot.sh
# Override depth:   MAX_DEPTH=3 bash /scripts/extract-cli-snapshot.sh
#
# Outputs JSON to stdout. Env vars are NOT included (extracted separately
# from upstream source code by extract-env-vars.sh).

set -euo pipefail

# Suppress color, update checks, and telemetry for deterministic output.
export NO_COLOR=1
export STEAMPIPE_UPDATE_CHECK=false STEAMPIPE_TELEMETRY=none
export POWERPIPE_UPDATE_CHECK=false POWERPIPE_TELEMETRY=none
export TERM=dumb

readonly CLI="${CLI_BIN:-steampipe}"
readonly MAX_DEPTH="${MAX_DEPTH:-4}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Strip ANSI escape sequences from stdin.
_strip_ansi() {
  sed 's/\x1b\[[0-9;]*[mGKHF]//g'
}

# Emit clean --help text for a command.
# Exits non-zero if the command itself fails (not just "no subcommands").
_help() {
  "$@" --help 2>&1 | _strip_ansi
}

# Parse subcommand names from help text on stdin.
# Prints one name per line; empty output (exit 0) = no Available Commands section.
_parse_subcommands() {
  awk '
    /^[[:space:]]*Available Commands:/ { in_section=1; next }
    in_section && /^[^[:space:]]/ { exit }
    in_section && /^[[:space:]]+[a-z]/ { print $1 }
  ' | grep -xv 'help' || true
}

# ---------------------------------------------------------------------------
# Recursive emitter
# ---------------------------------------------------------------------------

# Emit one JSON fragment per command visited (flags + help hash), then recurse.
# Args: depth  key_prefix  [cmd_words...]
_emit() {
  local depth="$1"
  local key_prefix="$2"
  shift 2
  # $@ = full command words, e.g.: steampipe service start

  # Capture help text ONCE; derive flags, subcommands, and hash from it.
  local help_text
  if ! help_text=$(_help "$@"); then
    return 0  # command failed — skip without poisoning the snapshot
  fi

  local flags
  flags=$(printf '%s\n' "$help_text" \
    | grep -oE -- '--[a-z][a-z0-9-]+' \
    | sort -u \
    | jq -R . | jq -s . \
    || printf '[]')

  local hash
  hash=$(printf '%s' "$help_text" | sha256sum | awk '{print $1}')

  jq -n \
    --arg kf "${key_prefix}_flags" \
    --argjson vf "$flags" \
    --arg kh "${key_prefix}_help_hash" \
    --arg vh "$hash" \
    '{($kf): $vf, ($kh): $vh}'

  [[ "$depth" -ge "$MAX_DEPTH" ]] && return 0

  local subcmds
  subcmds=$(printf '%s\n' "$help_text" | _parse_subcommands) || return 0

  while IFS= read -r sub; do
    [[ -z "$sub" ]] && continue
    _emit $(( depth + 1 )) "${key_prefix}_${sub}" "$@" "$sub"
  done <<< "$subcmds"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

VERSION=$("$CLI" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || printf 'unknown')

# Capture top-level help once.
TOP_HELP=$(_help "$CLI")
TOP_HASH=$(printf '%s' "$TOP_HELP" | sha256sum | awk '{print $1}')
TOP_CMDS=$(printf '%s\n' "$TOP_HELP" | _parse_subcommands)
SUBCMDS_JSON=$(printf '%s\n' "$TOP_CMDS" | jq -R . | jq -s .)

# Stream all JSON fragments then merge into one object.
{
  jq -n \
    --arg version   "$VERSION" \
    --arg date      "$(date -u +%Y-%m-%d)" \
    --arg help_hash "$TOP_HASH" \
    --argjson subs  "$SUBCMDS_JSON" \
    '{version: $version, snapshot_date: $date, help_text_hash: $help_hash, subcommands: $subs}'

  while IFS= read -r cmd; do
    [[ -z "$cmd" ]] && continue
    _emit 1 "$cmd" "$CLI" "$cmd"
  done <<< "$TOP_CMDS"

} | jq -s 'reduce .[] as $item ({}; . + $item)'
