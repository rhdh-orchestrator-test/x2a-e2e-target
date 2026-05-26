---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up a Chef server with a single admin user and organization, configuring system parameters and installing the necessary components.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with a single admin user and organization

- **Chef Infra Server**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with a single admin user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates an admin user with the specified username, name, email, and password
   - Creates an organization and associates the admin user with it
   - Generates PEM files for the user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates an admin user with the specified username, name, email, and password
   - Creates an organization and associates the admin user with it
   - Generates PEM files for the user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for hostname configuration

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
- **Usage context**: This credential is used as the password for the Chef Automate and Chef Infra Server admin user

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `${username}.pem` - Admin user PEM file
- `${orgname}-validator.pem` - Organization validator PEM file

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (bash scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization

# File verification
ls -la ${username}.pem  # Should exist
ls -la ${orgname}-validator.pem  # Should exist

# Service connectivity
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/_status  # Should return status information

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Chef server API check
knife user list -s https://localhost/organizations/${orgname} -k ${username}.pem -u ${username}
```