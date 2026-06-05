---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
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
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (this is a standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the deployment script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account for authentication to Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `jtonello.pem` (or configured username.pem) - User key file
- `lab-validator.pem` (or configured orgname-validator.pem) - Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (this script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/health

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl user-show jtonello  # Replace with configured username

# Organization verification
sudo chef-server-ctl org-list  # Should include the configured organization
sudo chef-server-ctl org-show lab  # Replace with configured organization name

# Key files
ls -la jtonello.pem  # Replace with configured username
ls -la lab-validator.pem  # Replace with configured organization name

# Network listening
sudo netstat -tulpn | grep LISTEN
sudo ss -tulpn | grep LISTEN

# Service status
sudo systemctl status chef-automate
sudo journalctl -u chef-automate

# Web UI access
curl -k https://localhost/  # Should redirect to login page

# API access (using the generated key)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Replace with configured values
```