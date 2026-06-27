---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, file operations, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
     - Username, full name, email, and password are configurable
     - Saves user key to a .pem file
   - Creates initial organization
     - Organization short name and full name are configurable
     - Associates the admin user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl commands (2)

The alternative script (`setup-automate/deploy-chef-server.sh`) performs similar operations but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None explicitly defined
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Automate/Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `${username}.pem` (Admin user key file)
- `${orgname}-validator.pem` (Organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None explicitly defined in the scripts

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status
systemctl status chef-automate

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# API connectivity
curl -k https://localhost/api/v0/auth/version

# Web UI accessibility
curl -k -I https://localhost

# Certificate verification
openssl x509 -in /var/opt/chef-automate/cert/HOSTNAME.crt -text -noout

# Log files
sudo tail -f /var/log/chef-automate/*.log

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Disk space
df -h /var/opt/chef-automate/

# Memory usage
free -m
```