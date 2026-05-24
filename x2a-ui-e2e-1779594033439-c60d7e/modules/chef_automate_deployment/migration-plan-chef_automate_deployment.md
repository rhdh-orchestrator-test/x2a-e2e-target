---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of Bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts configure system settings, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username: Configurable (default: 'jtonello')
     - Full name: Configurable (default: 'John Tonello')
     - Email: Configurable (default: 'jtonello@chef.lab')
     - Password: Configurable (default: 'password')
     - Generates user key file: <username>.pem
   - Creates a Chef organization with:
     - Organization name: Configurable (default: 'lab')
     - Full name: Configurable (default: 'Chef Lab')
     - Associates the created user with the organization
     - Generates organization validator key file: <orgname>-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The `deploy-chef-server.sh` script follows a similar pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (these are standalone Bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

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
- **Usage context**: This credential is used as the password for the Chef user created during the setup process.

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `<username>.pem` - User key file generated during setup
- `<orgname>-validator.pem` - Organization validator key file generated during setup

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UIs)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (the scripts don't use templates)

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
sudo chef-server-ctl user-show <username>  # Should show user details

# Organization verification
sudo chef-server-ctl org-list  # Should include the configured organization name
sudo chef-server-ctl org-show <orgname>  # Should show organization details

# Key files
ls -la <username>.pem  # Should exist and have proper permissions
ls -la <orgname>-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate and Chef Infra Server listening
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost  # Should return Chef Automate web UI
curl -k https://localhost/_status  # Should return status information

# Log files
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-automate logs  # Alternative way to check logs

# Service health
sudo chef-automate service-versions  # Check versions of all services
sudo chef-automate status  # Check status of all services
```