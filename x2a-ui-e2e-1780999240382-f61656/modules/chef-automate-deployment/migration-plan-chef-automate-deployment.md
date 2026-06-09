---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two Bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (HTTPS)
  - Key Config: Deployed with Chef Infra Server product
  
- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (HTTPS)
  - Key Config: Created with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two Bash scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate with Infra Server using the CLI
   - Creates an initial user with specified credentials
   - Creates an initial organization and associates the user with it
   - Resources: system configuration (2), file download (1), command execution (3)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) using the CLI
   - Creates an initial user with specified credentials
   - Creates an initial organization and associates the user with it
   - Resources: system configuration (2), file download (1), command execution (3)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `chef-automate` executable in the current directory
- User PEM file (e.g., `jtonello.pem`)
- Organization validator PEM file (e.g., `lab-validator.pem`)

**Service endpoints to check**:
- Chef Automate web UI (https://hostname)
- Chef Infra Server API (https://hostname/organizations/orgname)

**Templates rendered**: No templates are rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la chef-automate
./chef-automate version

# Chef Automate status (if deployed with deploy-automate.sh)
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
ls -la jtonello.pem  # or the configured username.pem
ls -la lab-validator.pem  # or the configured orgname-validator.pem

# Chef Server API access test
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Web UI access
curl -k https://localhost/api/v0/auth/version  # Chef Automate API check

# Service status
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Network listening
sudo netstat -tulpn | grep -E '443|80'
sudo ss -tlnp | grep -E '443|80'

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50
sudo chef-server-ctl tail

# Disk usage
df -h /var/opt/chef-automate
df -h /var/opt/chef-server
```