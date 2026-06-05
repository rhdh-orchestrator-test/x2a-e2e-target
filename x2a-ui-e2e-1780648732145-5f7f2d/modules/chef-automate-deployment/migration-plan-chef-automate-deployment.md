---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with customizable user and organization settings, and performs necessary system tuning for optimal performance.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Single instance deployment
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Installed on the local system alongside Chef Automate
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the following attributes:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Generates user key file (default: 'jtonello.pem')
   - Creates a Chef organization with the following attributes:
     - Organization short name (default: 'lab')
     - Organization full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Generates organization validator key file (default: 'lab-validator.pem')
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected in the deployment script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword` (set to 'password' by default)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded in script
- **Usage context**: Used to create the initial Chef user account for accessing Chef Infra Server and Chef Automate

## Checks for the Migration

**Files to verify**:
- User key file: `<username>.pem` (default: jtonello.pem)
- Organization validator key file: `<orgname>-validator.pem` (default: lab-validator.pem)
- Chef Automate configuration: `/etc/chef-automate/config.toml`

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly defined in the script. The Chef Automate deployment tool handles template rendering internally.

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list  # Should include the configured username
ls -la /path/to/user/key/file  # Should exist and have proper permissions

# Verify organization creation
sudo chef-server-ctl org-list  # Should include the configured organization
ls -la /path/to/org/validator/key/file  # Should exist and have proper permissions

# Verify web UI access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/_status  # Should return status information

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
```