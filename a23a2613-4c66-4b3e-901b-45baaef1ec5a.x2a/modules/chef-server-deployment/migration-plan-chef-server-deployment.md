# Migration Plan: chef-server-deployment

**TLDR**: This module deploys a Chef Infra Server using a bash script. It configures system settings, downloads and installs Chef Infra Server, creates a user, and sets up an organization. The script is designed for deployment on an on-premises or cloud VM.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server)

**Configured Instances**:

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default Chef Server ports (443, 80)
  - Key Config: System settings for vm.max_map_count and vm.dirty_expire_centisecs

## File Structure

```
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the value specified in the variables section
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Infra Server Installation** (`setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI tool
   - Extracts and makes it executable
   - Deploys Chef Infra Server with acceptance of terms and MLSA
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-chef-server.sh`):
   - Creates a Chef user with specified credentials:
     - Username: jtonello
     - Full name: John Tonello
     - Email: jtonello@chef.lab
     - Password: password
     - Saves private key to jtonello.pem
   - Creates a Chef organization:
     - Short name: lab
     - Full name: Chef Lab
     - Associates the created user with the organization
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

## Dependencies

**External dependencies**: None explicitly defined in the script
**System package dependencies**: curl, gunzip (implied by script usage)
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname change)
- jtonello.pem (user private key)
- lab-validator.pem (organization validator key)
- Chef Infra Server configuration files (in default locations)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS), 80 (HTTP)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly defined in the script. The Chef Infra Server installation handles its own templating.

## Pre-flight checks:
```bash
# System configuration
hostname  # Should return automate.chef.lab
sysctl vm.max_map_count  # Should return vm.max_map_count = 262144
sysctl vm.dirty_expire_centisecs  # Should return vm.dirty_expire_centisecs = 20000

# Chef Infra Server status
sudo chef-server-ctl status
systemctl status chef-server

# Network listening
netstat -tulpn | grep -E '443|80'
ss -tlnp | grep -E '443|80'

# User and organization verification
sudo chef-server-ctl user-list  # Should include jtonello
sudo chef-server-ctl org-list  # Should include lab

# Key files
ls -la jtonello.pem  # Should exist
ls -la lab-validator.pem  # Should exist

# API connectivity
curl -k https://localhost/_status  # Should return Chef Infra Server status
curl -k https://localhost/organizations/lab  # Should verify organization exists

# Chef Server version
chef-server-ctl version

# Chef Server configuration
chef-server-ctl show-config

# Logs
sudo tail -f /var/log/chef-server/nginx/access.log
sudo tail -f /var/log/chef-server/nginx/error.log
sudo tail -f /var/log/chef-server/bookshelf/current
sudo tail -f /var/log/chef-server/erchef/current
```