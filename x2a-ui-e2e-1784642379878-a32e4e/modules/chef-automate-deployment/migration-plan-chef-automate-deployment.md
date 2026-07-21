---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates a user and organization.

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

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the value specified in the hostname variable (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username: Variable 'username' (default: 'jtonello')
     - Full name: Variable 'longusername' (default: 'John Tonello')
     - Email: Variable 'useremail' (default: 'jtonello@chef.lab')
     - Password: Variable 'userpassword' (default: 'password')
     - Saves user key to a PEM file named after the username
   - Creates a Chef organization with:
     - Short name: Variable 'orgname' (default: 'lab')
     - Full name: Variable 'longorgname' (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a PEM file named after the organization
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, bash
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword` (set to 'password' by default)
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User and Organization Keys

- **Variable(s)**: `userfilename` (set to "${username}.pem"), `orgfilename` (set to "${orgname}-validator.pem")
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Generated during installation and saved to local files
- **Usage context**: Authentication keys for Chef user and organization validator

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly rendered in the script. Chef Automate handles its own template rendering internally.

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the created username
ls -la ${username}.pem  # Should exist and have proper permissions

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization
ls -la ${orgname}-validator.pem  # Should exist and have proper permissions

# Web UI access
curl -k https://localhost  # Should return Chef Automate login page

# API access
curl -k https://localhost/organizations/${orgname}  # Should return 401 Unauthorized (authentication required)

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep 443  # Alternative to netstat

# Logs
sudo chef-automate logs  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs
```