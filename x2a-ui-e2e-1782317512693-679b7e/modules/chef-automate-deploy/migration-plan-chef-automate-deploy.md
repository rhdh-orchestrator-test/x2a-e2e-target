---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's central server for managing infrastructure
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the main script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the hostname using `hostnamectl set-hostname`
   - Configures kernel parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified username, name, email, and password
   - Creates a Chef organization with specified name
   - Associates the user with the organization
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The second script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, bash
**Service dependencies**: None explicitly defined, but Chef Automate has its own service dependencies

## Credentials

**Detection Summary**: 5 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated and saved to local file system
- **Usage context**: Authentication key for the Chef user

### Chef Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated and saved to local file system
- **Usage context**: Authentication key for the Chef organization

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `${username}.pem` (user authentication key)
- `${orgname}-validator.pem` (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UIs)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

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
ls -la $userfilename

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
ls -la $orgfilename

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
```