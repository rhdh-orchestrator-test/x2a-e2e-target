---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts for deploying Chef Automate and Chef Infra Server. The scripts set up the Chef infrastructure components on a VM, configure hostname and system parameters, and create initial user and organization.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: A combined deployment of Chef Automate and Chef Infra Server
  - Location/Path: Deployed on the local system
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, and organization details

- **Chef Infra Server (standalone)**: A standalone deployment of Chef Infra Server
  - Location/Path: Deployed on the local system
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two shell scripts that deploy Chef infrastructure components:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates an initial user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization authentication
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates an initial user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization authentication
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (Chef Automate CLI handles installation)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user authentication key)
- ~/${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status (for deploy-automate.sh)
sudo chef-automate status
curl -k https://localhost/api/v0/auth/version  # Check Automate API
sudo chef-automate license status  # Check license status

# Chef Infra Server status (for both scripts)
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization
sudo chef-server-ctl user-show $username  # Check user details

# Authentication key verification
ls -la ~/$userfilename  # Check user key exists
ls -la ~/$orgfilename  # Check organization validator key exists

# Network listening
netstat -tulpn | grep 443  # Check HTTPS port
ss -tlnp | grep 443

# Service health
curl -k https://localhost/api/v0/health  # Check Automate health endpoint
sudo chef-automate diagnostics run  # Run diagnostics

# Logs
sudo chef-automate logs
sudo journalctl -u chef-automate
```