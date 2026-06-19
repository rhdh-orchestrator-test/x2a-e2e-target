---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup. The main features include system tuning, downloading and installing Chef Automate CLI, deploying Chef products, and creating initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Includes Chef Infra Server product

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
   - Tunes kernel parameters for optimal performance:
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
   - Creates a Chef user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Generates user key file (default: 'jtonello.pem')
   - Creates a Chef organization with:
     - Organization short name (default: 'lab')
     - Organization full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Generates organization validator key file (default: 'lab-validator.pem')
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own service dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account for authentication to Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Infra Server configuration directory)
- User key file (default: jtonello.pem)
- Organization validator key file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly rendered by the scripts. Chef Automate and Chef Infra Server handle their own template rendering internally.

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

# Chef Automate API check
curl -k https://localhost/api/v0/auth/version

# Chef Infra Server API check
curl -k https://localhost/organizations

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la jtonello.pem
chmod 400 jtonello.pem

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem
chmod 400 lab-validator.pem

# Test API access with user key
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service logs
sudo journalctl -u chef-automate
sudo chef-automate logs

# Chef Infra Server logs
sudo chef-server-ctl tail

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/opscode

# Memory usage
free -m
ps aux | grep chef | sort -rn -k 4 | head -10
```