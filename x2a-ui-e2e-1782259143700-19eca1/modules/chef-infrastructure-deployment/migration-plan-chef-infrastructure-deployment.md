---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef infrastructure deployment module consisting of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the specified products, and create a user and organization.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:
- **Chef Automate with Infra Server**: Deployed via deploy-automate.sh
  - Hostname: automate.chef.lab (configurable)
  - Components: Chef Automate + Chef Infra Server
  - User: jtonello (configurable)
  - Organization: lab (configurable)

- **Chef Infra Server**: Deployed via deploy-chef-server.sh
  - Hostname: automate.chef.lab (configurable)
  - Components: Chef Infra Server only
  - User: jtonello (configurable)
  - Organization: lab (configurable)

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with --accept-terms-and-mlsa=true
   - Creates a user with the configured username, name, email, and password
   - Creates an organization with the configured name and associates the user
   - Generates PEM files for the user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Infra Server only with --accept-terms-and-mlsa=true
   - Creates a user with the configured username, name, email, and password
   - Creates an organization with the configured name and associates the user
   - Generates PEM files for the user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for hostnamectl

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
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces by default

**Templates rendered**: None (no Chef templates used)

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

# PEM files verification
ls -la ~/*.pem
ls -la ~/*-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/_status

# Chef Automate UI access
curl -k -I https://localhost

# Chef Infra Server API access
knife user list -s https://localhost/organizations/lab -k ~/${username}.pem -u ${username}
```