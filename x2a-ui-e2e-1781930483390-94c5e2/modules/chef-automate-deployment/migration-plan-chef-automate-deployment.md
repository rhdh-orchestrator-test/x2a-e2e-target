---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts for deploying Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the specified products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed via Chef Automate CLI
  - Key Config: Requires system parameter adjustments (vm.max_map_count, vm.dirty_expire_centisecs)
  
- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed via Chef Automate CLI
  - Key Config: Integrated with Chef Automate in one script, standalone in another

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The module consists of two shell scripts that perform similar operations:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

Both scripts use the same set of variables:
- hostname: 'automate.chef.lab'
- username: 'jtonello'
- longusername: 'John Tonello'
- useremail: 'jtonello@chef.lab'
- userpassword: 'password'
- orgname: 'lab'
- longorgname: 'Chef Lab'

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for hostname setting

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
- User PEM file (named after the username, e.g., jtonello.pem)
- Organization validator PEM file (named after the organization, e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI)
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
ls -la jtonello.pem

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
curl -k https://localhost

# Service health
curl -k https://localhost/_status
```