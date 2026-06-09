---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up a Chef server environment with user and organization configuration. No actual Chef recipes are present in this module.

## Service Type and Instances

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate Server**: A single instance of Chef Automate with integrated Chef Infra Server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A standalone Chef Infra Server option (without Automate)
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform the following operations:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate with integrated Chef Infra Server
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for user and organization authentication

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal Chef Server performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only the Chef Infra Server component (without Automate)
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for user and organization authentication

Both scripts use the following configuration variables:
- hostname: The hostname for the Chef server
- username: Chef admin username
- longusername: Full name of the admin user
- useremail: Email address for the admin user
- userpassword: Password for the admin user
- orgname: Short name for the Chef organization
- longorgname: Full name of the Chef organization

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/hostname
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
cat /etc/hosts | grep $(hostname)
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status (if deployed with Automate)
sudo chef-automate status
curl -k https://localhost/api/_status

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl test

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
journalctl -u chef-automate -f

# API connectivity test
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem --no-editor
```