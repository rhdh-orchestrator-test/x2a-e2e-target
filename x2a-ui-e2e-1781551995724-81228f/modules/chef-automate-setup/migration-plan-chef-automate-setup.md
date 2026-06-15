---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-setup

**TLDR**: This module consists of bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial user and organization.

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

The module consists of bash scripts rather than Chef recipes. These scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates initial user with specified credentials:
     - Username, full name, email, password
     - Saves user key to [username].pem
   - Creates initial organization:
     - Organization short name, full name
     - Associates with created user
     - Saves organization validator key to [orgname]-validator.pem
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates initial user with specified credentials:
     - Username, full name, email, password
     - Saves user key to [username].pem
   - Creates initial organization:
     - Organization short name, full name
     - Associates with created user
     - Saves organization validator key to [orgname]-validator.pem
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None (these are standalone bash scripts)
**System package dependencies**: bash, curl, sudo
**Service dependencies**: None explicitly defined (Chef Automate handles its own dependencies)

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Chef Admin User Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated and saved to file
- **Usage context**: Authentication key for the admin user, saved to [username].pem

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated and saved to file
- **Usage context**: Organization validator key, saved to [orgname]-validator.pem

### Chef User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Email address for the admin user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- [username].pem (user key file)
- [orgname]-validator.pem (organization validator key file)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (these are bash scripts, not Chef templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/auth/version  # Should return version info

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# Key files
ls -la ${username}.pem  # Should exist and have proper permissions
ls -la ${orgname}-validator.pem  # Should exist and have proper permissions

# Network listening
sudo netstat -tulpn | grep ':443'  # Should show Chef Automate/Infra Server listening
sudo ss -tlnp | grep ':443'  # Alternative check for listening ports

# Service health
curl -k https://localhost/api/v0/health  # Chef Automate health endpoint
knife ssl check -s https://localhost/organizations/${orgname}  # Chef Infra Server SSL check

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-automate logs  # Alternative way to check logs

# Resources
sudo chef-automate status  # Shows component status
free -m  # Check memory usage
df -h  # Check disk usage
```