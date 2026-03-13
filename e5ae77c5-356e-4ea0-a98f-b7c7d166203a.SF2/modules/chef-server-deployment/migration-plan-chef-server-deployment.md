# Migration Plan: Chef Server Deployment

**TLDR**: This module deploys a Chef Infra Server on a VM using a bash script. It configures system parameters, downloads and installs Chef Server, creates a user, and sets up an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server)

**Configured Instances**:
- **Chef Infra Server**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for HTTPS)
  - Key Config: System parameters (vm.max_map_count=262144, vm.dirty_expire_centisecs=20000)

## File Structure

```
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The bash script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the specified value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Server Installation** (`setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI tool
   - Extracts and makes it executable
   - Deploys Chef Infra Server with acceptance of terms and MLSA
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-chef-server.sh`):
   - Creates a user with specified details:
     - Username, full name, email, password
     - Saves user key to a .pem file
   - Creates an organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

## Dependencies

**External cookbook dependencies**: None explicitly defined in the script
**System package dependencies**: curl, gunzip (implied by script usage)
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)
- Chef Server configuration files (standard locations)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (default)

**Templates rendered**:
- No templates are explicitly rendered in this script

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Server status
sudo chef-server-ctl status
systemctl status chef-server

# User verification
sudo chef-server-ctl user-list
sudo chef-server-ctl user-show jtonello  # Replace with actual username

# Organization verification
sudo chef-server-ctl org-list
sudo chef-server-ctl org-show lab  # Replace with actual org name

# Key files
ls -la jtonello.pem  # Replace with actual username
ls -la lab-validator.pem  # Replace with actual org name

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# API connectivity test
curl -k https://localhost/_status
curl -k https://automate.chef.lab/_status  # Replace with actual hostname

# Logs
sudo chef-server-ctl tail
sudo journalctl -u chef-server -f

# Resource usage
df -h
free -m
top -n 1
```