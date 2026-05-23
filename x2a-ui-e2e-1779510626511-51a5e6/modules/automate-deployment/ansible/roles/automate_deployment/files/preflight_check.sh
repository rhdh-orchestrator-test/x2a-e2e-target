#!/bin/bash
# Preflight check script for Chef Automate and Chef Infra Server deployment

echo "Running preflight checks for Chef Automate deployment..."

# Check system memory
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
echo "Total memory: ${TOTAL_MEM}MB"
if [ ${TOTAL_MEM} -lt 8192 ]; then
  echo "WARNING: Chef Automate recommends at least 8GB of RAM"
fi

# Check disk space
ROOT_DISK=$(df -h / | awk 'NR==2 {print $4}')
echo "Available disk space: ${ROOT_DISK}"

# Check kernel parameters
MAX_MAP_COUNT=$(sysctl -n vm.max_map_count)
echo "vm.max_map_count: ${MAX_MAP_COUNT}"
if [ ${MAX_MAP_COUNT} -lt 262144 ]; then
  echo "WARNING: vm.max_map_count should be at least 262144"
fi

DIRTY_EXPIRE=$(sysctl -n vm.dirty_expire_centisecs)
echo "vm.dirty_expire_centisecs: ${DIRTY_EXPIRE}"
if [ ${DIRTY_EXPIRE} -lt 20000 ]; then
  echo "WARNING: vm.dirty_expire_centisecs should be at least 20000"
fi

# Check required ports
echo "Checking if required ports are available..."
for PORT in 80 443 9631; do
  if netstat -tuln | grep -q ":${PORT} "; then
    echo "WARNING: Port ${PORT} is already in use"
  else
    echo "Port ${PORT} is available"
  fi
done

# Check hostname resolution
echo "Checking hostname resolution..."
HOSTNAME=$(hostname -f)
if host "${HOSTNAME}" &>/dev/null; then
  echo "Hostname ${HOSTNAME} resolves correctly"
else
  echo "WARNING: Hostname ${HOSTNAME} does not resolve"
fi

echo "Preflight checks completed"