---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in the main script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates an initial admin user with specified credentials
   - Creates an initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates an initial admin user with specified credentials
   - Creates an initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial admin user in Chef Infra Server

### Admin User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial admin user in Chef Infra Server

### User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated during execution and saved to file
- **Usage context**: Authentication key for the admin user

### Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated during execution and saved to file
- **Usage context**: Authentication key for the organization validator

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `$userfilename` (user PEM file in the current directory)
- `$orgfilename` (organization validator PEM file in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System hostname
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
ls -la $userfilename
ls -la $orgfilename

# Test API access with the generated credentials
knife user list -s https://$hostname/organizations/$orgname -u $username -k $userfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
systemctl status chef-server

# Logs
sudo journalctl -u chef-automate -n 100
sudo journalctl -u chef-server -n 100

# Web UI access
curl -k https://localhost/api/v0/status
```