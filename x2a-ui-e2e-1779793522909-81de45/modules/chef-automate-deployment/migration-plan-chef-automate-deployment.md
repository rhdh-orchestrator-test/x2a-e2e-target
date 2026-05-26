---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Configuration Management Platform

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Includes Chef Infra Server integration

- **Chef Infra Server**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
     - Username, full name, email, and password are configurable
     - Saves user key to a PEM file
   - Creates initial organization
     - Organization short name and full name are configurable
     - Associates the admin user with the organization
     - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (this is a standalone script)
**System package dependencies**: curl, sudo, hostnamectl, sysctl
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `$userfilename` (default: jtonello.pem) - User key file
- `$orgfilename` (default: lab-validator.pem) - Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (this is a deployment script, not a Chef cookbook)

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

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Verify key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Check Chef Automate UI access
curl -k https://localhost/api/v0/auth/version

# Check Chef Infra Server API access
curl -k https://localhost/organizations/lab

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Logs
sudo chef-automate logs
sudo chef-server-ctl tail

# Verify deployment
sudo chef-automate verify
```