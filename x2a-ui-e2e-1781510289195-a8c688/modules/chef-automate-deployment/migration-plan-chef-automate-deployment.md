---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using bash scripts. It configures a single instance with user and organization creation. The deployment is done through the Chef Automate CLI tool.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, chmod (2)

3. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI tool
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

4. **User Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a user in Chef Infra Server with:
     - Username (e.g., 'jtonello')
     - Full name (e.g., 'John Tonello')
     - Email (e.g., 'jtonello@chef.lab')
     - Password (e.g., 'password')
   - Saves user key to a PEM file (e.g., 'jtonello.pem')
   - Resources: chef-server-ctl user-create (1)

5. **Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates an organization in Chef Infra Server with:
     - Short name (e.g., 'lab')
     - Full name (e.g., 'Chef Lab')
   - Associates the previously created user with the organization
   - Saves organization validator key to a PEM file (e.g., 'lab-validator.pem')
   - Resources: chef-server-ctl org-create (1)

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same steps but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef Infra Server admin user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment uses CLI tools rather than templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la jtonello.pem
chmod 400 jtonello.pem  # Ensure proper permissions

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem
chmod 400 lab-validator.pem  # Ensure proper permissions

# API connectivity test
knife user list -s https://automate.chef.lab/organizations/lab -k jtonello.pem -u jtonello

# Web UI access
curl -k https://automate.chef.lab/api/v0/auth/version
curl -k https://automate.chef.lab/api/v0/health

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Service status
sudo systemctl status chef-automate
sudo chef-server-ctl service-list

# Logs
sudo journalctl -u chef-automate -f
sudo chef-server-ctl tail

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/chef-server
```