---
source-path: setup-automate
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization settings

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization settings

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Makes the CLI executable
   - Deploys Chef Automate and Chef Infra Server:
     - Runs `./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Creates initial user:
     - Runs `chef-server-ctl user-create` with username, full name, email, password
     - Saves user key to a .pem file
   - Creates initial organization:
     - Runs `chef-server-ctl org-create` with org name, full org name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy command (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Makes the CLI executable
   - Deploys Chef Infra Server only (without Automate):
     - Runs `./chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`
   - Creates initial user:
     - Runs `chef-server-ctl user-create` with username, full name, email, password
     - Saves user key to a .pem file
   - Creates initial organization:
     - Runs `chef-server-ctl org-create` with org name, full org name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy command (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (Chef Automate handles its own dependencies)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: 
  - setup-automate/deploy-automate.sh
  - setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user with `chef-server-ctl user-create`

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (e.g., jtonello.pem in the current directory)
- Organization validator PEM file (e.g., lab-validator.pem in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la chef-automate
./chef-automate version

# Service status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443
lsof -i :443

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
```