---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization settings

- **Chef Infra Server**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server product bundle
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Generates user key file (default: 'jtonello.pem')
   - Creates organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates admin user with organization
     - Generates organization validator key (default: 'lab-validator.pem')
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

4. **Alternative Deployment - Chef Infra Server Only** (`setup-automate/deploy-chef-server.sh`):
   - Similar to the main script but only deploys Chef Infra Server without Automate
   - Uses the same system configuration and user/organization setup steps
   - Resources: Same as above, but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial admin user in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- Generated PEM files:
  - User key file (default: jtonello.pem)
  - Organization validator key (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname (default: automate.chef.lab)
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username (default: jtonello)
sudo chef-server-ctl org-list  # Should include the configured organization (default: lab)

# Key files
ls -la jtonello.pem  # Should exist and have proper permissions
ls -la lab-validator.pem  # Should exist and have proper permissions

# Web UI accessibility
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/organizations/lab  # Should verify Chef Infra Server API endpoint

# Network listening
netstat -tulpn | grep 443  # Should show services listening on port 443
ss -tlnp | grep 443  # Alternative check for services listening on port 443

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate system-logs  # View Chef Automate system logs
```