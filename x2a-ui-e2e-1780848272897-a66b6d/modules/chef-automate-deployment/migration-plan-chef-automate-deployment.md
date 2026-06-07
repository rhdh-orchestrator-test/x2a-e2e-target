---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, configure system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443
  - Key Config: Deployed with Chef Infra Server product

- **Chef Infra Server**:
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443
  - Key Config: Integrated with Chef Automate or standalone

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Deploys Chef Automate with Infra Server using the CLI
   - Creates initial user with specified username, name, email, and password
   - Creates initial organization with specified name and associates it with the user
   - Generates PEM files for user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate CLI, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Deploys only Chef Infra Server (without Automate) using the CLI
   - Creates initial user with specified username, name, email, and password
   - Creates initial organization with specified name and associates it with the user
   - Generates PEM files for user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate CLI, chef-server-ctl (2)

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
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)
- Chef Automate configuration files (generated during deployment)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:
```bash
# Hostname configuration
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# PEM files
ls -la ~/$userfilename
ls -la ~/$orgfilename

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl list-units --type=service | grep chef
systemctl status chef-automate

# Logs
sudo journalctl -u chef-automate -f
sudo chef-automate system-logs
```