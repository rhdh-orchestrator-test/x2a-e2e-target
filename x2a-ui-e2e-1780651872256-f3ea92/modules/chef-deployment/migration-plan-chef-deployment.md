---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the products, and create a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate and Chef Infra Server**: Deployed together on a single VM
  - Location/Path: Local system
  - Port/Socket: Default ports (Chef Automate UI typically uses 443)
  - Key Config: VM hostname, user creation, organization creation

- **Chef Infra Server**: Standalone deployment option
  - Location/Path: Local system
  - Port/Socket: Default ports (typically 443)
  - Key Config: VM hostname, user creation, organization creation

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Saves user and organization validator keys to files
   - Resources: sysctl (2), curl/gunzip (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Saves user and organization validator keys to files
   - Resources: sysctl (2), curl/gunzip (1), chef-automate deploy (1), chef-server-ctl (2)

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
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user

## Checks for the Migration

**Files to verify**:
- User key file: `<username>.pem` (default: jtonello.pem)
- Organization validator key file: `<orgname>-validator.pem` (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files existence
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://automate.chef.lab/api/_status

# Chef Server API accessibility
curl -k https://automate.chef.lab/organizations/lab

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service logs
sudo journalctl -u chef-automate -f
sudo chef-automate system-logs

# Hostname verification
hostname
cat /etc/hostname
```