---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: Deployed via deploy-automate.sh
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (Chef Automate UI)
  - Key Config: Sets hostname, system parameters, and creates initial user/organization

- **Chef Infra Server (standalone)**: Deployed via deploy-chef-server.sh
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (Chef Server API)
  - Key Config: Sets hostname, system parameters, and creates initial user/organization

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

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
- Ports listening: 443 (Chef Automate UI and Chef Server API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

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

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/_status

# Chef Automate UI access
curl -k https://localhost/

# Log verification
sudo journalctl -u chef-automate
```