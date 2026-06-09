---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a single instance of Chef Automate with integrated Chef Infra Server, configures system parameters, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Main Chef Automate server instance
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Integrated Chef Infra Server
  - Location/Path: Installed alongside Chef Automate
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

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
   - Downloads the Chef Automate CLI tool from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates an initial user with the configured username, name, email, and password
   - Saves the user's private key to a .pem file
   - Creates an organization with the configured name
   - Associates the created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None (this script installs the services)

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef Automate/Infra Server admin user

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Infra Server configuration directory)
- ${username}.pem (User key file)
- ${orgname}-validator.pem (Organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None (script uses CLI tools to deploy and configure)

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

# Web UI accessibility
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/organizations/$orgname

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50
sudo chef-automate system-logs
```