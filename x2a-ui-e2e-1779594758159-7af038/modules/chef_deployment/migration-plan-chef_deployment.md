---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A complete Chef automation platform
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization

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
   - Downloads Chef Automate CLI
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a Chef user with specified username, name, email, and password
   - Creates a Chef organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, Chef user, Chef organization

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a Chef user with specified username, name, email, and password
   - Creates a Chef organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, Chef user, Chef organization

Both scripts use the same set of variables:
- hostname: 'automate.chef.lab'
- username: 'jtonello'
- longusername: 'John Tonello'
- useremail: 'jtonello@chef.lab'
- userpassword: 'password'
- orgname: 'lab'
- longorgname: 'Chef Lab'
- userfilename: "${username}.pem"
- orgfilename: "${orgname}-validator.pem"

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password
- **Variable(s)**: `userpassword`
- **Source file(s)**: 
  - setup-automate/deploy-automate.sh
  - setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user PEM file)
- ${orgname}-validator.pem (organization validator PEM file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
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

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/_status

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
```