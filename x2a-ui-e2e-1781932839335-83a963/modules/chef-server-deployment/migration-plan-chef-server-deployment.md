---
source-path: setup-automate
---

# Migration Plan: setup-automate (Chef Server Deployment)

**TLDR**: This is a simple bash script that deploys Chef Infra Server on a Linux system. It sets system parameters, downloads and installs Chef Server, and configures a user and organization. No actual Chef cookbook is present - just deployment scripts.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server)

**Configured Instances**:
- **Chef Infra Server**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization creation

## File Structure

```
deploy-chef-server.sh
deploy-automate.sh
```

## Module Explanation

The module consists of two bash scripts that perform similar operations. I'll focus on the `deploy-chef-server.sh` script as requested:

1. **System Configuration** (`deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Server Installation** (`deploy-chef-server.sh`):
   - Downloads Chef Automate CLI tool
   - Deploys Chef Infra Server using the CLI tool
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`deploy-chef-server.sh`):
   - Creates a user with specified credentials
     - Username, full name, email, and password are configurable
     - Saves user key to a .pem file
   - Creates an organization
     - Organization short name and full name are configurable
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (this is a script, not a cookbook)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Server Admin Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Server

## Checks for the Migration

**Files to verify**:
- `/etc/hosts` (for hostname configuration)
- `$userfilename` (default: jtonello.pem) - User key file
- `$orgfilename` (default: lab-validator.pem) - Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Server status
sudo chef-server-ctl status
curl -k https://localhost/_status  # Should return Chef Server status

# User verification
sudo chef-server-ctl user-list  # Should include the configured username
ls -la jtonello.pem  # Or whatever $userfilename is set to
sudo chef-server-ctl user-show jtonello  # Replace with actual username

# Organization verification
sudo chef-server-ctl org-list  # Should include the configured organization name
ls -la lab-validator.pem  # Or whatever $orgfilename is set to
sudo chef-server-ctl org-show lab  # Replace with actual organization name

# Service status
sudo systemctl status chef-server
sudo chef-server-ctl service-list

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Logs
sudo chef-server-ctl tail
sudo journalctl -u chef-server

# API connectivity test (using the created user key)
knife ssl check -c <(echo "
node_name 'jtonello'
client_key '$(pwd)/jtonello.pem'
chef_server_url 'https://automate.chef.lab/organizations/lab'
")
```