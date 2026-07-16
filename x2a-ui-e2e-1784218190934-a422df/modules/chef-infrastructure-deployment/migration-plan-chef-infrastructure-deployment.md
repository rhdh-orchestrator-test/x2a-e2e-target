---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the specified products, and create a user and organization.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: Deployed via deploy-automate.sh
  - Location/Path: Installed on the local system
  - Key Config: Sets hostname, system parameters, and creates initial user/organization

- **Chef Infra Server (standalone)**: Deployed via deploy-chef-server.sh
  - Location/Path: Installed on the local system
  - Key Config: Sets hostname, system parameters, and creates initial user/organization

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
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
- ~/${username}.pem (user PEM file)
- ~/${orgname}-validator.pem (organization validator PEM file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameter verification
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

# PEM file verification
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/_status

# Chef Server API check
knife user list -s https://localhost/organizations/lab -u jtonello -k ~/jtonello.pem

# Chef Automate UI access
curl -k -I https://localhost
```