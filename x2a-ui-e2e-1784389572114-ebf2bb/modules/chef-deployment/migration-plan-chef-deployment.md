---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef deployment script that installs and configures Chef Automate and Chef Infra Server on a VM. It consists of two bash scripts that set up either both Chef Automate and Chef Infra Server or just Chef Infra Server, along with creating an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook consists of two bash scripts that perform the following operations:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures kernel parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates an initial user with the configured username, name, email, and password
   - Creates an organization and associates the user with it
   - Saves the user and organization validator PEM files
   - Resources: bash script with system commands (hostnamectl, sysctl, curl, chef-automate, chef-server-ctl)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures kernel parameters for optimal Chef Server performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates an initial user with the configured username, name, email, and password
   - Creates an organization and associates the user with it
   - Saves the user and organization validator PEM files
   - Resources: bash script with system commands (hostnamectl, sysctl, curl, chef-automate, chef-server-ctl)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system packages)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should be set to the configured hostname)
- User PEM file (e.g., jtonello.pem in the current directory)
- Organization validator PEM file (e.g., lab-validator.pem in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status
curl -k https://localhost/api/v0/health

# Chef Server status
sudo chef-server-ctl status
sudo chef-server-ctl test

# User and organization verification
ls -la *.pem  # Should show user and org validator PEM files
knife user list -s https://localhost -u ADMIN_USERNAME -k USER.pem  # Replace with actual username and PEM file
knife org list -s https://localhost -u ADMIN_USERNAME -k USER.pem  # Replace with actual username and PEM file

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Service status
sudo systemctl status chef-automate  # If Chef Automate is installed
sudo systemctl status chef-server  # If Chef Server is installed

# Log files
sudo tail -f /var/log/chef-automate/*.log  # Chef Automate logs
sudo tail -f /var/log/opscode/*.log  # Chef Server logs

# Disk space
df -h  # Check available disk space
```