---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using a bash script. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
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
   - Creates an initial admin user with the following attributes:
     - Username: Configured value (default: 'jtonello')
     - Full name: Configured value (default: 'John Tonello')
     - Email: Configured value (default: 'jtonello@chef.lab')
     - Password: Configured value (default: 'password')
     - Saves user key to a .pem file
   - Creates an initial organization with the following attributes:
     - Organization short name: Configured value (default: 'lab')
     - Organization full name: Configured value (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for hostname configuration

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword` (set to 'password' by default)
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ${username}.pem (user key file, default: jtonello.pem)
- ${orgname}-validator.pem (organization validator key file, default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname (default: automate.chef.lab)
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate installation
chef-automate status  # Should show services running
curl -k https://localhost/api/v0/auth/version  # Should return Chef Automate version info

# Chef Infra Server
chef-server-ctl status  # Should show all services running
ls -la jtonello.pem  # Should exist and have proper permissions
ls -la lab-validator.pem  # Should exist and have proper permissions

# User and organization verification
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should show the created user
knife org list -s https://localhost -u jtonello -k jtonello.pem  # Should show the created organization

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep 443  # Alternative way to check listening ports
curl -k https://localhost/api/v0/auth/status  # Should return status OK

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate system-logs  # View Chef Automate system logs

# Service status
sudo systemctl status chef-automate  # Check Chef Automate service status
```