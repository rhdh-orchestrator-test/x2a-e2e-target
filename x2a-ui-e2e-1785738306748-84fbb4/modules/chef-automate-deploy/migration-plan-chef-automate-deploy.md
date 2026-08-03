---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server with a single command
   - Accepts terms and MLSA automatically
   - Resources: chef-automate deploy command with --product flags

4. **User Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a user in Chef Infra Server with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
   - Saves user key to a PEM file (default: 'jtonello.pem')
   - Resources: chef-server-ctl user-create

5. **Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates an organization in Chef Infra Server with:
     - Organization short name (default: 'lab')
     - Organization full name (default: 'Chef Lab')
   - Associates the previously created user with the organization
   - Saves organization validator key to a PEM file (default: 'lab-validator.pem')
   - Resources: chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (this is a standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Infra Server User Password

- **Variable(s)**: `userpassword` (set to 'password' by default)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- User key file: `[username].pem` (default: jtonello.pem)
- Organization validator key: `[orgname]-validator.pem` (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (script doesn't use templates)

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

# Verify Chef Automate UI is accessible
curl -k https://localhost  # Should return HTTP 200 or redirect to login page

# Verify Chef Infra Server API is accessible
curl -k https://localhost/organizations  # Should return a 401 Unauthorized (API exists but needs auth)

# Verify user creation
sudo chef-server-ctl user-list  # Should include the created username
ls -la /path/to/user.pem  # Verify user key file exists

# Verify organization creation
sudo chef-server-ctl org-list  # Should include the created organization
ls -la /path/to/org-validator.pem  # Verify organization validator key exists

# Test API access with the created user
knife user list -s https://localhost/organizations/ORGNAME -u USERNAME -k /path/to/user.pem

# Check logs
sudo chef-automate logs

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Service status
systemctl status chef-automate
```