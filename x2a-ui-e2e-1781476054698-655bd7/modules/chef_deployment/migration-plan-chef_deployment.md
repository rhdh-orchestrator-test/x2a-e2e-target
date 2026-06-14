---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure either Chef Automate with Chef Infra Server or just Chef Infra Server alone. The scripts set system parameters, download the Chef Automate CLI, deploy the selected products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: Deployed via deploy-automate.sh
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: User and organization creation

- **Chef Infra Server**: Deployed via deploy-chef-server.sh
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: User and organization creation

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with --accept-terms-and-mlsa=true
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI execution, user creation, organization creation

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with --accept-terms-and-mlsa=true
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI execution, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip (part of gzip package)
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (e.g., jtonello.pem in the current directory)
- Organization validator PEM file (e.g., lab-validator.pem in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:
```bash
# Hostname check
hostname
cat /etc/hostname

# System parameters check
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI check
ls -la chef-automate
./chef-automate version

# Service status (for Chef Automate with Infra Server)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files check
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-automate logs
journalctl -u chef-automate
```