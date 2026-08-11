---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts handle system prerequisites, download Chef Automate CLI, deploy the products, and set up initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for Chef Automate:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username, full name, email, password
     - Saves user key to a .pem file
   - Creates a Chef organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

4. **Chef Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Alternative script that deploys only Chef Infra Server without Automate
   - Follows the same steps as above but with `--product infra-server` only
   - Resources: Same as above but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef/
- Generated PEM files: `$username.pem` and `$orgname-validator.pem` in the current directory

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (uses Chef Automate's built-in templates)

## Pre-flight checks:
```bash
# System configuration checks
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate service status
sudo chef-automate status

# Chef Server service status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list | grep $username

# Verify organization creation
sudo chef-server-ctl org-list | grep $orgname

# Check PEM files
ls -la $username.pem
ls -la $orgname-validator.pem

# Verify Chef Automate UI is accessible
curl -k https://localhost/api/v0/auth/version

# Test Chef Server API
knife ssl check -c /etc/chef/client.rb

# Check listening ports
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Check logs
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail

# Verify user can authenticate
knife user list -u $username -k $username.pem -s https://localhost/organizations/$orgname

# Check system resources
df -h
free -m
top -bn1 | head -20
```