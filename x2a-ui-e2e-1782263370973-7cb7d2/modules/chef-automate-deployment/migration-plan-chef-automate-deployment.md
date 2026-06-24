---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Resources: curl, chmod commands

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flags

4. **Chef Infra Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates initial user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Saves user key to a .pem file
   - Creates initial organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates the created user
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo
**Service dependencies**: None explicitly defined, but requires proper network configuration and sufficient system resources

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used as the password for the initial Chef Infra Server user

## Checks for the Migration

**Files to verify**:
- User key file: `<username>.pem` (default: jtonello.pem)
- Organization validator key file: `<orgname>-validator.pem` (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (bash scripts don't use templates)

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

# Service connectivity
curl -k https://localhost
curl -k https://automate.chef.lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Chef Infra Server API test (using the created user key)
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem

# Chef Automate API test
curl -k https://automate.chef.lab/api/v0/auth/version
```