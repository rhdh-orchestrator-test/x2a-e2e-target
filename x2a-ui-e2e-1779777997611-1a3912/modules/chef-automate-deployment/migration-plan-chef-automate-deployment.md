---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

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

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user with the following attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Generates user key file: jtonello.pem
   - Creates an organization with the following attributes:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user
     - Generates organization validator key: lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

4. **Chef Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Alternative script that deploys only Chef Infra Server without Automate
   - Uses the same configuration parameters and user/org setup
   - Only difference is the `--product` flag in the deployment command
   - Resources: Same as above but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
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
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Server configuration directory)
- Generated PEM files: jtonello.pem, lab-validator.pem

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for both Chef Automate UI and Chef Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment uses CLI tools rather than templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate API check
curl -k https://localhost/api/v0/auth/version

# Chef Server API check
curl -k https://localhost/organizations/lab

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Test API access with generated credentials
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Logs
sudo journalctl -u chef-automate
sudo chef-automate logs

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Process verification
ps aux | grep chef
```