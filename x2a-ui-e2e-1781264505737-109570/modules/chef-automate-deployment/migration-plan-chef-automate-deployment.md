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

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Generates user key file (default: 'jtonello.pem')
   - Creates a Chef organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates the created user
     - Generates organization validator key (default: 'lab-validator.pem')
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

4. **Chef Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Alternative script that deploys only Chef Infra Server without Automate
   - Uses the same configuration parameters and user/org setup
   - Only difference is the `--product` flag in the deployment command
   - Resources: Same as above, but with different chef-automate deploy parameters

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

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostnamectl (hostname configuration)
- /etc/sysctl.conf (kernel parameters)
- Chef Automate configuration files (locations determined by Chef Automate installer)
- User and organization PEM files:
  - jtonello.pem (or configured username)
  - lab-validator.pem (or configured organization name)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are explicitly rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/health  # Should return healthy status

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization

# Verify PEM files
ls -la jtonello.pem  # Should exist and have proper permissions
ls -la lab-validator.pem  # Should exist and have proper permissions

# Test API access
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should return user list without errors

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Server listening
ss -tlnp | grep 443  # Alternative check for listening ports

# Service status
systemctl list-units --type=service | grep chef  # Should show Chef services
journalctl -u chef-automate  # Check Chef Automate logs

# Web UI access
curl -k -I https://localhost  # Should return HTTP 200 OK
```