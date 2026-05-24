---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup, system tuning, and required components for Chef infrastructure management.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Includes Chef Infra Server integration

- **Chef Infra Server**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of bash scripts that deploy Chef Automate and Chef Infra Server. There are no Chef recipes in this module, but rather shell scripts that install and configure the Chef infrastructure components.

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures system kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate with Infra Server using the CLI tool
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: sysctl (2), curl download (1), chef-automate deploy (1), chef-server-ctl commands (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value
   - Configures system kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server using the CLI tool
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: sysctl (2), curl download (1), chef-automate deploy (1), chef-server-ctl commands (2)

## Dependencies

**External cookbook dependencies**: None (uses bash scripts, not Chef cookbooks)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined (Chef Automate handles its own dependencies)

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (uses Chef Automate's built-in templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# Chef Server API access
curl -k https://localhost/organizations/lab

# Log verification
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/chef-server

# Service health
sudo chef-automate service-versions
sudo chef-automate preflight-check
```