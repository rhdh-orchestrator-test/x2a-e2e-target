---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure Chef Automate and Chef Infra Server on a Linux system, create a user, and create an organization.

## Service Type and Instances

**Service Type**: Chef Infrastructure Management (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate and Chef Infra Server**: Deployed on a single host
  - Location/Path: Local system
  - Port/Socket: Default ports (443 for Chef Automate UI)
  - Key Config: User and organization creation

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
   - Deploys Chef Automate and Chef Infra Server with accepted terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for the user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with accepted terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for the user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for hostname setting

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the Chef user account

### User PEM Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef user

### Organization Validator PEM Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef organization

### User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (bash scripts only)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname

# PEM key files
ls -la ~/${username}.pem
ls -la ~/${orgname}-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/health

# Chef Server API access
knife user list -s https://localhost/organizations/${orgname} -k ~/${username}.pem -u ${username}

# Service status
systemctl status chef-automate
```