---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a single instance of Chef Automate with integrated Chef Infra Server, configures system parameters, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Single instance deployment with integrated Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: System parameters (vm.max_map_count=262144, vm.dirty_expire_centisecs=20000)

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
   - Extracts and makes the binary executable
   - Deploys Chef Automate with integrated Chef Infra Server
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
   - Creates organization and associates the admin user
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but deploys only Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
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
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (script-based deployment)

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
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/v0/health

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Chef Server API check (using the generated admin key)
knife user list -s https://localhost/organizations/lab -u jtonello -k ~/jtonello.pem

# Chef Automate API token generation test
sudo chef-automate iam token create admin --admin
```