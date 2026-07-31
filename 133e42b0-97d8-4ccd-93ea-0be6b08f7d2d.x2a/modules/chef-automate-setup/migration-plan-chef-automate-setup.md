---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-setup

**TLDR**: This is a bash script-based deployment of Chef Automate and Chef Infra Server. It sets up a single instance of Chef Automate with Chef Infra Server, creates an initial admin user, and configures an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname set to value in script variable

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the same system as Chef Automate
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the value specified in the `hostname` variable
   - Configures kernel parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads the Chef Automate CLI tool from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates an initial admin user with:
     - Username from `username` variable
     - Full name from `longusername` variable
     - Email from `useremail` variable
     - Password from `userpassword` variable
     - Saves user key to `$username.pem` file
   - Creates an organization with:
     - Short name from `orgname` variable
     - Full name from `longorgname` variable
     - Associates the admin user with the organization
     - Saves organization validator key to `$orgname-validator.pem` file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (this is a standalone bash script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: This credential is used to set the initial password for the Chef Automate and Chef Infra Server admin user

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `$username.pem` (Admin user key file in current directory)
- `$orgname-validator.pem` (Organization validator key in current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None (deployment uses Chef Automate's built-in configuration)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate service status
sudo chef-automate status

# Chef Automate API check
curl -k https://localhost/api/v0/auth/version

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname

# Key files
ls -la $username.pem
ls -la $orgname-validator.pem

# Test API access with the generated key
knife user list -s https://localhost/organizations/$orgname -u $username -k $username.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Logs
sudo chef-automate system-logs
sudo chef-server-ctl tail

# Service status
sudo systemctl status chef-automate
```