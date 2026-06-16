---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a Bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate, and configures a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the hostname using `hostnamectl set-hostname`
   - Configures kernel parameters with `sysctl`:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the `--product automate --product infra-server` flags
   - Accepts terms and MLSA
   - Resources: curl command, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with `chef-server-ctl user-create`
     - Username, full name, email, and password are configured
     - Generates a user key file (PEM)
   - Creates a Chef organization with `chef-server-ctl org-create`
     - Organization short name and full name are configured
     - Associates the created user with the organization
     - Generates an organization validator key file (PEM)
   - Resources: chef-server-ctl commands (2)

## Dependencies

**External dependencies**: 
- Chef Automate CLI (downloaded from packages.chef.io)
- Chef Infra Server (installed as part of the deployment)

**System package dependencies**: 
- curl
- gunzip
- sudo

**Service dependencies**: 
- None explicitly defined in the script

## Credentials

**Detection Summary**: 3 credentials detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated PEM file
- **Usage context**: Authentication key for the Chef user

### Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated PEM file
- **Usage context**: Authentication key for the Chef organization

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `~/${username}.pem` (user key file)
- `~/${orgname}-validator.pem` (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
- No templates are explicitly rendered in this script

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
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl user-show $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
sudo chef-server-ctl org-show $orgname

# Key files
ls -la ~/$userfilename
ls -la ~/$orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/health

# Log verification
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Version verification
sudo chef-automate version
```