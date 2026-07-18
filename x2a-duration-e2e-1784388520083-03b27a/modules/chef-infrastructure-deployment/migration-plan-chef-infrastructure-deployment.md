---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module deploys Chef Automate and Chef Infra Server infrastructure using shell scripts. It configures system parameters, downloads and installs Chef Automate CLI, deploys either both Chef Automate and Chef Infra Server or just Chef Infra Server, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Infrastructure Management Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI package and makes it executable
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a Chef user with the specified username, name, email, and password
   - Creates a Chef organization and associates the created user with it
   - Generates PEM key files for the user and organization
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI package and makes it executable
   - Deploys only Chef Infra Server (without Automate) with the `--accept-terms-and-mlsa=true` flag
   - Creates a Chef user with the specified username, name, email, and password
   - Creates a Chef organization and associates the created user with it
   - Generates PEM key files for the user and organization
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be set to 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be set to 20000)
- chef-automate executable in the deployment directory
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user and organization
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Check PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Verify web UI accessibility
curl -k https://localhost/_status
curl -k https://localhost/organizations/lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Chef server logs
sudo chef-server-ctl tail

# Verify API access using the created user
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Verify Chef Automate API
curl -k https://localhost/api/v0/auth/version
```