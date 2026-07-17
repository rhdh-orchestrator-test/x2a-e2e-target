---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script repository for Chef Automate and Chef Infra Server, containing two bash scripts that install and configure these components on a Linux system. The scripts set up a Chef server with a single admin user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The repository contains two shell scripts that perform similar operations:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and installs Chef Automate CLI
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates an admin user with specified credentials
   - Creates an organization and associates the admin user
   - Resources: sysctl (2), curl/download (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server product (without Automate)
   - Creates an admin user with specified credentials
   - Creates an organization and associates the admin user
   - Resources: sysctl (2), curl/download (1), chef-automate deploy (1), chef-server-ctl (2)

Both scripts use the following configuration variables:
- hostname: 'automate.chef.lab'
- username: 'jtonello'
- longusername: 'John Tonello'
- useremail: 'jtonello@chef.lab'
- userpassword: 'password'
- orgname: 'lab'
- longorgname: 'Chef Lab'

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly configured

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (admin user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

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
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health
curl -k https://localhost/api/_status
curl -k https://localhost/organizations/lab

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
```