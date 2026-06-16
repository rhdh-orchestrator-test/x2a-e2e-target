---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module deploys Chef Infra Server and Chef Automate on a single VM. It configures system settings, downloads and installs Chef components, creates a user, and sets up an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server and Chef Automate)

**Configured Instances**:

- **Chef Infra Server**: Core Chef server component
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization creation

- **Chef Automate**: Chef's observability and automation platform
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Infra Server

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef products with acceptance of terms and MLSA
     - deploy-automate.sh: Deploys both Automate and Infra Server
     - deploy-chef-server.sh: Deploys only Infra Server
   - Resources: curl, chmod, chef-automate deploy (1)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Creates a user with the following attributes:
     - Username: jtonello
     - Full name: John Tonello
     - Email: jtonello@chef.lab
     - Password: password
     - Saves user key to jtonello.pem
   - Creates an organization with the following attributes:
     - Short name: lab
     - Full name: Chef Lab
     - Associates with user jtonello
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate and Chef Infra Server have their own dependencies

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
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count
- /proc/sys/vm/dirty_expire_centisecs
- jtonello.pem (user key file)
- lab-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (no templates used in this module)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hosts | grep automate.chef.lab
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/health

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test API access with the created user
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-automate logs
sudo chef-server-ctl tail
journalctl -u chef-automate -f
```