---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Platform

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Includes Chef Infra Server in deploy-automate.sh

- **Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Can be deployed standalone via deploy-chef-server.sh

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/hostname
- User PEM file (default: jtonello.pem)
- Organization validator PEM file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly rendered in the scripts. The Chef Automate deployment process handles template rendering internally.

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
cat /etc/hosts | grep automate.chef.lab
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health checks
curl -k https://localhost/api/v0/health

# Chef Server API check (using the generated PEM file)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Chef Automate UI accessibility
curl -k -I https://localhost

# Log verification
sudo journalctl -u chef-automate
sudo chef-automate logs

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/chef
```