---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **chef-automate**: Chef Automate server with integrated Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI, 9631 for service communication)
  - Key Config: System parameters (vm.max_map_count=262144, vm.dirty_expire_centisecs=20000)

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl to the configured hostname value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the following attributes:
     - Username, full name, email, and password
     - Saves user key to a PEM file
   - Creates a Chef organization with:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate has its own service management

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
- **Usage context**: This credential is used to set the initial password for the Chef admin user created during setup

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml
- /etc/opscode/chef-server.rb
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI), 9631 (Chef Automate services)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment scripts don't use templates)

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

# Verify Chef Automate UI is accessible
curl -k https://localhost

# Verify Chef user
sudo chef-server-ctl user-list | grep jtonello

# Verify Chef organization
sudo chef-server-ctl org-list | grep lab

# Verify PEM files exist and have correct permissions
ls -la jtonello.pem
ls -la lab-validator.pem

# Check Chef Automate services
sudo systemctl status chef-automate
sudo journalctl -u chef-automate

# Check Chef Server services
sudo chef-server-ctl service-list
sudo chef-server-ctl status

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 9631

# Logs
sudo journalctl -u chef-automate -f
sudo tail -f /var/log/chef-server/nginx/access.log
sudo tail -f /var/log/chef-server/nginx/error.log

# API connectivity test (using the created user's PEM file)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Verify Chef Automate API
curl -k https://localhost/api/v0/auth/version

# Check disk space
df -h /var/opt/chef-automate
df -h /var/opt/opscode

# Memory usage
free -m
ps aux | grep chef | awk '{print $6/1024 " MB\t" $11}'
```