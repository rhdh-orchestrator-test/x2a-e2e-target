---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the specified products, and create a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Chef's central server for managing infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, user creation, organization creation

2. **deploy-chef-server.sh**:
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, user creation, organization creation

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

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- ${username}.pem (user authentication key)
- ${orgname}-validator.pem (organization validation key)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# Hostname configuration
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la ./jtonello.pem
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la ./lab-validator.pem
sudo chef-server-ctl org-show lab

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
ss -tulpn | grep 443
curl -k https://localhost

# Authentication test
knife user list -s https://localhost/organizations/lab -u jtonello -k ./jtonello.pem

# Web UI access
curl -k https://localhost/
```