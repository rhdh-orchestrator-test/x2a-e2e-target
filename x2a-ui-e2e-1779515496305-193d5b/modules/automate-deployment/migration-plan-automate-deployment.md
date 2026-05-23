---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring system parameters, installing Chef Automate CLI, deploying Chef products, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (typically 443)
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
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server products
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command

4. **User Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
   - Saves user key to a PEM file
   - Resources: chef-server-ctl user-create

5. **Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial organization with specified:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
   - Associates the created user with the organization
   - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl org-create

Note: There is also a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following the same steps but with a different deployment command.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: This credential is used as the password for the initial Chef admin user created during deployment

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user key file, default: jtonello.pem)
- ${orgname}-validator.pem (organization validator key file, default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (script doesn't use templates)

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

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
```