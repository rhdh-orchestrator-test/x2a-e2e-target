---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deploy

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Server

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate with integrated Chef Infra Server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A standalone Chef Infra Server (in the second script)
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate with integrated Chef Infra Server
   - Creates an initial admin user with specified credentials
   - Creates an initial organization and associates the admin user
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, Chef Automate CLI, Chef Server CTL

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate)
   - Creates an initial admin user with specified credentials
   - Creates an initial organization and associates the admin user
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, Chef Automate CLI, Chef Server CTL

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/hosts` (hostname should be set correctly)
- `chef-automate` executable in the directory where the script was run
- User PEM file (e.g., `jtonello.pem`) in the directory where the script was run
- Organization validator PEM file (e.g., `lab-validator.pem`) in the directory where the script was run

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System hostname check
hostname
hostnamectl status | grep "Static hostname"

# Kernel parameter checks
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI availability
ls -la ./chef-automate
./chef-automate version

# Chef Automate status
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
ls -la ./${username}.pem
ls -la ./${orgname}-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Service status
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Log files
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50
sudo tail -f /var/log/chef-automate/automate.log 2>/dev/null || echo "Log file not found"
sudo tail -f /var/log/chef-server/server.log 2>/dev/null || echo "Log file not found"

# API check (requires valid token)
# Get a token first (interactive)
# TOKEN=$(sudo chef-automate admin-token)
# curl -k -H "api-token: $TOKEN" https://localhost/api/v0/auth/users
```