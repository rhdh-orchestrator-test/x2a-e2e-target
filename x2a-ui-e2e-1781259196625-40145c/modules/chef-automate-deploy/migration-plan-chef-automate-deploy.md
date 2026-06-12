---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the main script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl command, chmod command, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified username, full name, email, and password
   - Creates a Chef organization with specified name and description
   - Associates the user with the organization
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own service dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `$userfilename` (User PEM file in current directory)
- `$orgfilename` (Organization validator PEM file in current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly rendered in the scripts. Chef Automate handles its own templating internally.

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate API and UI
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost

# Chef Infra Server API
curl -k https://localhost/organizations

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# PEM files
ls -la $userfilename
ls -la $orgfilename

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Logs
sudo chef-automate system-logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# Health check
sudo chef-automate health check
sudo chef-server-ctl test

# Version information
sudo chef-automate version
sudo chef-server-ctl version
```