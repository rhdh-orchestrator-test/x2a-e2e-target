---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a Linux system. It configures system parameters, downloads and installs Chef Automate CLI, deploys the Chef Automate and Infra Server products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Deployed with default configuration

- **Chef Infra Server**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with custom user and organization

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, chmod, chef-automate deploy

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
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User and Organization Keys

- **Variable(s)**: `userfilename="${username}.pem"`, `orgfilename="${orgname}-validator.pem"`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated files
- **Usage context**: Authentication keys for Chef user and organization validator

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- Generated PEM files: 
  - User key file (default: jtonello.pem)
  - Organization validator key file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list  # Should include the configured username
ls -la ${username}.pem  # Should exist and have proper permissions

# Verify organization creation
sudo chef-server-ctl org-list  # Should include the configured organization
ls -la ${orgname}-validator.pem  # Should exist and have proper permissions

# Verify web UI access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/organizations/${orgname}  # Should verify Chef Infra Server organization

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service logs
sudo journalctl -u chef-automate -n 100
sudo chef-automate logs

# Verify Chef Automate API
curl -k https://localhost/api/v0/auth/version
```