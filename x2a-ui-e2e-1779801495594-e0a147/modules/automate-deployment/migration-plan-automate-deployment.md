---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with default settings

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of bash scripts that perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the CLI executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
     - Username, full name, email, and password are configurable
     - Saves user key to a .pem file
   - Creates initial organization
     - Organization short name and full name are configurable
     - Associates admin user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same process but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined (Chef Automate manages its own services)

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate/Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Infra Server configuration directory)
- ${username}.pem (Admin user key file)
- ${orgname}-validator.pem (Organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment uses Chef Automate CLI which handles template rendering internally)

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

# Service status
systemctl status chef-automate
systemctl list-units 'chef-*'

# API connectivity - Chef Automate
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# API connectivity - Chef Infra Server
curl -k https://localhost/organizations
curl -k --key /path/to/${username}.pem --cert /path/to/${username}.pem https://localhost/organizations/${orgname}

# User verification
sudo chef-server-ctl user-list | grep ${username}
sudo chef-server-ctl org-list | grep ${orgname}

# Logs
sudo journalctl -u chef-automate -f
sudo chef-automate system-logs

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Configuration files
sudo ls -la /etc/chef-automate/
sudo ls -la /etc/opscode/

# PEM files
ls -la ${username}.pem
ls -la ${orgname}-validator.pem
file ${username}.pem
file ${orgname}-validator.pem

# Disk space
df -h /var/opt/chef-automate/
df -h /var/opt/opscode/

# Memory usage
free -m
ps aux | grep chef | awk '{print $6/1024 " MB\t" $11}'
```