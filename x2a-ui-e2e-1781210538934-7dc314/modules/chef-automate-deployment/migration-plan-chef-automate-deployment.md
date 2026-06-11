---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server on a VM. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the specified products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Chef's policy and configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the value specified in the variables section
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Extracts and makes executable
   - Deploys Chef Automate and Chef Infra Server:
     - Uses `./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Creates initial user:
     - Uses `chef-server-ctl user-create` with username, full name, email, password
     - Saves user key to a .pem file
   - Creates initial organization:
     - Uses `chef-server-ctl org-create` with org name, full org name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the value specified in the variables section
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Extracts and makes executable
   - Deploys only Chef Infra Server (without Automate):
     - Uses `./chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`
   - Creates initial user:
     - Uses `chef-server-ctl user-create` with username, full name, email, password
     - Saves user key to a .pem file
   - Creates initial organization:
     - Uses `chef-server-ctl org-create` with org name, full org name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are directly rendered by these scripts.

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
sudo chef-server-ctl org-show lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/_status

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Service health
sudo chef-automate service-versions
sudo chef-server-ctl service-list

# Disk usage
df -h /var/opt/chef-automate
df -h /var/opt/chef-server
```