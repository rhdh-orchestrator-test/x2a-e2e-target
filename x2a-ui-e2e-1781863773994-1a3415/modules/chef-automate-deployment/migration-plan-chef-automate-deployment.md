---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **automate.chef.lab**: Single Chef Automate and Chef Infra Server instance
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for Chef Automate UI, 8989 for Chef Infra Server)
  - Key Config: 
    - System parameters: vm.max_map_count=262144, vm.dirty_expire_centisecs=20000
    - User: jtonello
    - Organization: lab

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to 'automate.chef.lab'
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates user 'jtonello' with specified details:
     - Full name: John Tonello
     - Email: jtonello@chef.lab
     - Password: password
     - Saves user key to jtonello.pem
   - Creates organization 'lab' with specified details:
     - Full name: Chef Lab
     - Associates with user 'jtonello'
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) performs similar operations but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip (part of gzip package)
**Service dependencies**: None explicitly defined, but Chef Automate has its own service dependencies

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
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef/
- jtonello.pem (in the directory where the script is run)
- lab-validator.pem (in the directory where the script is run)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI), 8989 (Chef Infra Server)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment uses Chef's built-in templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate UI access
curl -k https://localhost/api/v0/health

# Chef Infra Server access
sudo chef-server-ctl test

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep -E '443|8989'
ss -tlnp | grep -E '443|8989'

# Logs
sudo chef-automate logs
sudo journalctl -u chef-server
sudo chef-server-ctl tail

# API check with user key
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Organization validation
knife client list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# System resources
df -h
free -m
top -n 1
```