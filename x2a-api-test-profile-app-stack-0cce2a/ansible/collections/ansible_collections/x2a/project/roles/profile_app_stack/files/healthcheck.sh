#!/usr/bin/env bash
set -euo pipefail

url="${1:?health-check URL is required}"
curl --fail --silent --show-error --max-time 10 "$url" >/dev/null
