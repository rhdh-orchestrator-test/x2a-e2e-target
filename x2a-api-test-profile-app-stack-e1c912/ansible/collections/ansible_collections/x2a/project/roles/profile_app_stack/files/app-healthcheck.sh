#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--push-metrics" ]]; then
    exit 0
fi

url="${1:-http://localhost:8000/health}"
curl --fail --silent --show-error --max-time 10 "${url}" >/dev/null
