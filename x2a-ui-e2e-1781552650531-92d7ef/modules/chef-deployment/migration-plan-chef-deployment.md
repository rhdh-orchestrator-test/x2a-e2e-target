---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is not a Chef cookbook but rather a set of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the Chef infrastructure components with configurable user, organization, and hostname parameters.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:
- **Chef Automate Server**: A complete infrastructure automation platform
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a Chef user with the configured credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for the user and organization
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal Chef Server performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates a Chef user with the configured credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for the user and organization
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

Both scripts use the same set of configurable variables:
- hostname: The hostname for the Chef server (default: 'automate.chef.lab')
- username: Chef user's username (default: 'jtonello')
- longusername: Chef user's full name (default: 'John Tonello')
- useremail: Chef user's email (default: 'jtonello@chef.lab')
- userpassword: Chef user's password (default: 'password')
- orgname: Chef organization short name (default: 'lab')
- longorgname: Chef organization full name (default: 'Chef Lab')

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

### Chef User Password
- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/_status

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
```