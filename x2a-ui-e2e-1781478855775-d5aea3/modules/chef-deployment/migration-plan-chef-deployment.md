---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and deploy Chef Automate CLI, and configure users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A complete automation platform that includes Chef Infra Server, Chef Automate, and related components
  - Location/Path: Deployed on the local system
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Standalone Chef server deployment
  - Location/Path: Deployed on the local system
  - Key Config: Accepts terms and MLSA

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate with both automate and infra-server products
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI execution, user creation, organization creation

2. **deploy-chef-server.sh**:
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Infra Server only (without Automate)
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI execution, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
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
- **Usage context**: Used for creating a Chef user during deployment

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user PEM file)
- ${orgname}-validator.pem (organization validator PEM file)

**Service endpoints to check**:
- Chef Automate web interface (typically on port 443)
- Chef Infra Server API (typically on port 443)

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (if deploy-automate.sh was used)
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname

# PEM files
ls -la $userfilename
ls -la $orgfilename

# Network listening
ss -tulpn | grep 443

# Web interface accessibility
curl -k https://localhost

# Chef server API accessibility
curl -k https://localhost/organizations/$orgname
```