#!/usr/bin/env bash
# Extract environment variable names from upstream Steampipe source code.
# Runs on the CI runner (not inside the container).
#
# Usage:
#   bash scripts/extract-env-vars.sh 2.4.1
#
# Outputs a JSON array of env var names to stdout.

set -euo pipefail

VERSION="${1:?Usage: $0 <version>}"

# Fetch env.go from the tagged release
ENV_GO_URL="https://raw.githubusercontent.com/turbot/steampipe/v${VERSION}/pkg/constants/env.go"

ENV_VARS=$(curl -sfL "$ENV_GO_URL" \
  | grep -oE '"(STEAMPIPE_[A-Z_]+|PIPES_[A-Z_]+)"' \
  | tr -d '"' \
  | sort -u \
  | jq -R . | jq -s .)

if [ "$ENV_VARS" = "[]" ] || [ -z "$ENV_VARS" ]; then
  echo "ERROR: No env vars extracted from $ENV_GO_URL" >&2
  exit 1
fi

echo "$ENV_VARS"
