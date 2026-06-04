---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
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
   - Sets the hostname to the value specified in the hostname variable
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with the --accept-terms-and-mlsa flag
   - Resources: curl command, file permissions change, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the specified username, name, email, and password
   - Saves the user key to a .pem file
   - Creates a Chef organization with the specified organization name
   - Associates the user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External dependencies**: None specified in the script
**System package dependencies**: curl, gunzip (implied by the script's commands)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the Chef user account

## Checks for the Migration

**Files to verify**:
- User PEM file (dynamically named based on username variable)
- Organization validator PEM file (dynamically named based on orgname variable)
- Chef Automate configuration files (created during deployment)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are explicitly rendered in this script.

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
sudo chef-server-ctl user-list | grep $username
ls -la $userfilename

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
ls -la $orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Web UI access
curl -k https://localhost/api/_status

# Chef server API access
knife user list -s https://localhost/organizations/$orgname -k $userfilename -u $username

# Log verification
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Service status
systemctl status chef-automate
```