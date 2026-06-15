---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure Chef Automate and Chef Infra Server on a Linux system, create a user, and set up an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for authentication
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for authentication
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (Chef Automate handles its dependencies)
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
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (no templates used in this cookbook)

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
sudo chef-server-ctl user-list | grep $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname

# Key files
ls -la ~/$username.pem
ls -la ~/$orgname-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/v0/health

# Chef Server API check (using the created user key)
knife user list -s https://localhost/organizations/$orgname -u $username -k ~/$username.pem

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs
```