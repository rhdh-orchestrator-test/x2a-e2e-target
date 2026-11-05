#!/bin/sh
set -eu

if [ "${1:-}" = "--push-metrics" ]; then
    exec /usr/bin/curl --fail --silent --show-error \
      --data-binary "app_health 1\n" \
      "${PUSHGATEWAY_URL:-http://localhost:9091}/metrics/job/test-app"
fi

URL=${1:?health URL is required}
exec /usr/bin/curl --fail --silent --show-error "${URL}"
