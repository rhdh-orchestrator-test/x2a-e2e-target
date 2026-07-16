---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a Bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
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
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
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

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- User key file: `<username>.pem` (default: jtonello.pem)
- Organization validator key file: `<orgname>-validator.pem` (default: lab-validator.pem)
- Chef Automate configuration files (generated during deployment)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly in the script. Chef Automate deployment process handles its own templating.

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the created user (default: jtonello)
ls -la jtonello.pem  # Should exist and have proper permissions

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization (default: lab)
ls -la lab-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
curl -k https://localhost  # Should return Chef Automate login page

# Service health
sudo chef-automate service-versions  # Should show all service versions
sudo chef-server-ctl test  # Should pass all tests

# Logs
sudo chef-automate logs  # Check for any errors
sudo journalctl -u chef-automate  # Check systemd logs if applicable

# API connectivity test (using the created user key)
knife ssl check -c <path_to_knife_config>  # Should verify SSL connection
knife user list -c <path_to_knife_config>  # Should list users including the created one
```