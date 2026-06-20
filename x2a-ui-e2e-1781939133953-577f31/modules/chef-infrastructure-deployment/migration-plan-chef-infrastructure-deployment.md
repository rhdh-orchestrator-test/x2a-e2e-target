---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server. The scripts set up a Chef infrastructure environment with user and organization creation. No actual Chef cookbook structure is present.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for Automate UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server (standalone)**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for Chef Server UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two shell scripts that perform the following operations:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal Chef Server performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Infra Server only (without Automate) with acceptance of terms
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined, but requires standard Linux system services

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef administrator user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (shell scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files existence
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/_status

# Chef Server API check (using the created user key)
knife user list -s https://localhost/organizations/lab -u jtonello -k ~/jtonello.pem

# Chef Automate API check (if deployed)
curl -k https://localhost/api/v0/auth/version
```