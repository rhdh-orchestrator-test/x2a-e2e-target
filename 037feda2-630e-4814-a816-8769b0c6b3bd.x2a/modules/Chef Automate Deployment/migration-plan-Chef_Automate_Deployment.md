# Migration Plan: Chef Automate Deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using shell scripts. It configures a single instance with customizable user and organization settings, sets required system parameters, and performs post-installation configuration.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server with the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flags

4. **Chef Infra Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server with the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Creation** (Both scripts):
   - Creates a user with the configured details:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Saves user key to a .pem file
   - Creates an organization with the configured details:
     - Organization short name (default: 'lab')
     - Organization full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (uses shell scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/chef/[username].pem (default: /etc/chef/jtonello.pem)
- /etc/chef/[orgname]-validator.pem (default: /etc/chef/lab-validator.pem)
- chef-automate executable in the deployment directory

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0) or as configured by Chef Automate

**Templates rendered**:
- No templates are explicitly rendered in these scripts

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la chef-automate  # Should exist and be executable

# Service status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the configured username
ls -la /path/to/username.pem  # Should exist with proper permissions

# Organization verification
sudo chef-server-ctl org-list  # Should include the configured organization
ls -la /path/to/orgname-validator.pem  # Should exist with proper permissions

# Web UI access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/organizations  # Should return Chef Infra Server data

# Network listening
netstat -tulpn | grep 443  # Should show services listening on port 443
ss -tlnp | grep 443  # Alternative check for listening services

# Logs
sudo chef-automate logs  # Check for any errors
sudo chef-server-ctl tail  # Check Chef Infra Server logs
```