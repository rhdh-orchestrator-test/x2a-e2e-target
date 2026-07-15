---
source-path: setup-automate
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts configure system settings, download and install Chef Automate CLI, deploy the specified products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Creates user and organization with specified credentials

- **Chef Infra Server (standalone)**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Creates user and organization with specified credentials

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system settings:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Saves user and organization validator keys to files
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl commands

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system settings:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Saves user and organization validator keys to files
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl commands

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

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for system tuning parameter)
- /proc/sys/vm/dirty_expire_centisecs (for system tuning parameter)
- chef-automate executable in the deployment directory
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) or as configured in Chef Automate

**Templates rendered**: No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# System hostname check
hostname
hostnamectl

# System settings check
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI check
ls -la chef-automate
./chef-automate version

# Chef Automate status check
sudo ./chef-automate status

# Chef Infra Server service check
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files check
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility check
curl -k https://localhost/api/v0/health

# Network listening check
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs check
sudo ./chef-automate logs

# Deployment configuration check
sudo ./chef-automate config show
```