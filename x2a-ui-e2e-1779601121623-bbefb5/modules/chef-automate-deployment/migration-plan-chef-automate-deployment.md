---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using bash scripts. It configures system settings, downloads and installs Chef Automate CLI, deploys the selected products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with specified products (automate and infra-server)
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with chef-server-ctl
     - Username, full name, email, and password are configurable
     - Saves user key to a .pem file
   - Creates initial organization with chef-server-ctl
     - Organization short name and full name are configurable
     - Associates the admin user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

4. **Chef Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Alternative script that follows the same steps but only deploys the Chef Infra Server product
   - Omits the Chef Automate product during deployment
   - Otherwise identical to the main deployment script
   - Resources: Same as above but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None (this is the initial deployment)

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Initial admin user password for Chef Automate/Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (uses CLI commands rather than templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
which chef-automate
chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Web UI accessibility
curl -k https://localhost/  # Should return 200 OK
curl -k https://localhost/_status  # Should return status information

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization

# PEM files
ls -la /path/to/user.pem  # Should exist and have proper permissions
ls -la /path/to/org-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443
lsof -i :443

# Service logs
sudo journalctl -u chef-automate -f
sudo chef-automate system-logs

# Verify API access using the generated credentials
knife user list -s https://localhost/organizations/ORGNAME -u USERNAME --key /path/to/user.pem -k
```