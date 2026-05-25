---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Deploys Chef Automate with the automate and infra-server products
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username: configurable (default: 'jtonello')
     - Full name: configurable (default: 'John Tonello')
     - Email: configurable (default: 'jtonello@chef.lab')
     - Password: configurable (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name: configurable (default: 'lab')
     - Full name: configurable (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) performs similar operations but only deploys the Chef Infra Server product without Chef Automate.

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

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account for authentication to Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`: Chef Server configuration directory
- `/etc/chef/`: Chef client configuration directory
- User PEM file (default: jtonello.pem)
- Organization validator PEM file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (uses Chef Automate's built-in templates)

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

# Verify Chef user
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl user-show jtonello  # Replace with actual username

# Verify Chef organization
sudo chef-server-ctl org-list  # Should include the configured organization
sudo chef-server-ctl org-show lab  # Replace with actual organization name

# Verify PEM files
ls -la jtonello.pem  # Replace with actual username
ls -la lab-validator.pem  # Replace with actual organization name

# Test Chef Automate UI
curl -k https://localhost  # Should return HTTP 200 or redirect to login page

# Test Chef Infra Server API
curl -k https://localhost/organizations  # Should return a list of organizations

# Check services
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Check logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Verify knife commands work with the generated credentials
knife ssl fetch -s https://localhost
knife user list -s https://localhost -u jtonello -k jtonello.pem  # Replace with actual username and key
knife client list -s https://localhost -u jtonello -k jtonello.pem -o lab  # Replace with actual username, key, and organization
```