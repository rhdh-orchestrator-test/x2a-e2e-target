---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup. The scripts handle hostname configuration, system tuning, downloading the Chef Automate CLI, deploying the products, and creating initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **chef-automate**: Chef Automate server with integrated Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Chef Automate UI, 8989 for Chef Infra Server)
  - Key Config: Hostname, user creation, organization creation

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (e.g., 'jtonello')
     - Full name (e.g., 'John Tonello')
     - Email (e.g., 'jtonello@chef.lab')
     - Password (e.g., 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name (e.g., 'lab')
     - Full name (e.g., 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

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
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `~/${username}.pem` - User key file
- `~/${orgname}-validator.pem` - Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI), 8989 (Chef Infra Server)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None - this is a bash script that doesn't use templates

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
sudo chef-server-ctl user-show $username  # Should show user details

# Organization verification
sudo chef-server-ctl org-list  # Should include the configured organization
sudo chef-server-ctl org-show $orgname  # Should show organization details

# Key files
ls -la ~/$userfilename  # Should exist and have proper permissions
ls -la ~/$orgfilename  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443  # Chef Automate UI
netstat -tulpn | grep 8989  # Chef Infra Server

# Web UI access
curl -k https://localhost  # Should return Chef Automate UI content
curl -k https://localhost:8989  # Should return Chef Infra Server content

# API access (using the generated key)
knife user list -s https://localhost:8989 -u $username -k ~/$userfilename  # Should list users
knife org list -s https://localhost:8989 -u $username -k ~/$userfilename  # Should list organizations

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-automate system-logs  # Alternative way to check logs

# Service health
sudo chef-automate service-versions  # Check versions of all services
sudo chef-automate status  # Check status of all services
```