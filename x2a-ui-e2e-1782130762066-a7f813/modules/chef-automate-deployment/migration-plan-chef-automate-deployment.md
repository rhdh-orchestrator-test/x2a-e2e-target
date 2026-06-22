---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization. The script is not a Chef cookbook but a bash script that installs Chef products.

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
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username: Configured value (default: 'jtonello')
     - Full name: Configured value (default: 'John Tonello')
     - Email: Configured value (default: 'jtonello@chef.lab')
     - Password: Configured value (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization:
     - Org short name: Configured value (default: 'lab')
     - Org full name: Configured value (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None (this is a bash script, not a Chef cookbook)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user for authentication to Chef Infra Server and Chef Automate

## Checks for the Migration

**Files to verify**:
- `/etc/chef/jtonello.pem` (or the filename specified by `$userfilename`)
- `/etc/chef/lab-validator.pem` (or the filename specified by `$orgfilename`)
- Chef Automate configuration files (typically in `/etc/chef-automate/`)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (this is a bash script, not a Chef cookbook with templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/health  # Should return health status

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Key files
ls -la /path/to/jtonello.pem  # Should exist and have proper permissions
ls -la /path/to/lab-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 100
sudo chef-automate logs
sudo chef-server-ctl tail

# Web UI access
curl -k https://localhost/  # Should redirect to login page
```