---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a simple bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Deployed with Chef Infra Server product

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **Set Variables** (`setup-automate/deploy-automate.sh`):
   - Defines configuration variables: hostname, username, longusername, useremail, userpassword, orgname, longorgname
   - Sets dynamic variables: userfilename, orgfilename
   - Resources: Bash variables (7 user-configurable, 2 dynamic)

2. **Configure System** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl (1), sysctl (2)

3. **Download and Install Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes it executable
   - Resources: curl (1), file permissions (1)

4. **Deploy Chef Products** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

5. **Configure Chef Server** (`setup-automate/deploy-automate.sh`):
   - Creates a user with chef-server-ctl user-create
     - Username, full name, email, and password from variables
     - Saves user key to a .pem file
   - Creates an organization with chef-server-ctl org-create
     - Organization short name and full name from variables
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `${username}.pem` - User key file
- `${orgname}-validator.pem` - Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname

# Key files
ls -la $userfilename
ls -la $orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/v0/health

# Chef Server API check
knife user list -s https://localhost/organizations/$orgname -u $username -k $userfilename

# Logs
sudo chef-automate system-logs
sudo journalctl -u chef-automate
```