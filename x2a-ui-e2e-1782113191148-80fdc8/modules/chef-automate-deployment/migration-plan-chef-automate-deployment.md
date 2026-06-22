---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script-based deployment of Chef Automate and Chef Infra Server, not a Chef cookbook. The scripts configure hostname, system parameters, download and deploy Chef Automate CLI, and set up initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Platform

**Configured Instances**:

- **Chef Automate**: Central management platform for Chef
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (typically 443)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username: Configurable (default: 'jtonello')
     - Full name: Configurable (default: 'John Tonello')
     - Email: Configurable (default: 'jtonello@chef.lab')
     - Password: Configurable (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization:
     - Organization short name: Configurable (default: 'lab')
     - Organization full name: Configurable (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

The secondary script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys the Chef Infra Server component without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: This credential is used to set the initial password for the Chef admin user created during deployment

## Checks for the Migration

**Files to verify**:
- User key file: `[username].pem` (default: jtonello.pem)
- Organization validator key: `[orgname]-validator.pem` (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (not a Chef cookbook)

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

# User verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl user-show [username]  # Should show user details

# Organization verification
sudo chef-server-ctl org-list  # Should include the configured organization
sudo chef-server-ctl org-show [orgname]  # Should show organization details

# Key files
ls -la [username].pem  # Should exist
ls -la [orgname]-validator.pem  # Should exist

# Web UI access
curl -k https://localhost  # Should return Chef Automate UI HTML
curl -k https://localhost/_status  # Should return status information

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -f
sudo journalctl -u chef-server -f
```