---
source-path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two shell scripts for deploying Chef Automate and Chef Infra Server. The scripts configure system settings, download the Chef Automate CLI, deploy the specified products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two shell scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a Chef user with the specified username, name, email, and password
   - Creates a Chef organization and associates the created user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a Chef user with the specified username, name, email, and password
   - Creates a Chef organization and associates the created user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account with chef-server-ctl

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `~/${username}.pem` (user authentication key)
- `~/${orgname}-validator.pem` (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status
curl -k https://localhost/api/v0/auth/version  # Check Automate API
curl -k https://localhost  # Should return Chef Automate UI

# Chef Infra Server status (deployed by both scripts)
sudo chef-server-ctl status
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ~/${username}.pem  # Should show the created user
knife org list -s https://localhost -u ${username} -k ~/${username}.pem  # Should show the created organization

# Verify user and organization
sudo chef-server-ctl user-show ${username}
sudo chef-server-ctl org-show ${orgname}

# Check generated credential files
ls -la ~/${username}.pem  # Should exist
ls -la ~/${orgname}-validator.pem  # Should exist

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Service processes
ps aux | grep chef-server
ps aux | grep automate  # Only if deployed with deploy-automate.sh

# Logs
sudo journalctl -u chef-server
sudo journalctl -u automate  # Only if deployed with deploy-automate.sh
```