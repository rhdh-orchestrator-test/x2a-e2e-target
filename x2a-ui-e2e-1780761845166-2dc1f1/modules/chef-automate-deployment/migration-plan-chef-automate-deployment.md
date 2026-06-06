---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the same deployment

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
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
     - Organization short name (default: 'lab')
     - Organization full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Generates organization validator key file (default: 'lab-validator.pem')
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys the Chef Infra Server product without Chef Automate.

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

### Chef Admin User Password

- **Variable(s)**: `userpassword` (set to 'password')
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostnamectl (hostname configuration)
- User key file (default: jtonello.pem)
- Organization validator key file (default: lab-validator.pem)
- Chef Automate configuration files (installed by the deployment process)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly rendered in the scripts. The Chef Automate deployment process handles template rendering internally.

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/status  # Should return status information

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl test

# User and organization verification
sudo chef-server-ctl user-list  # Should include 'jtonello' or configured username
sudo chef-server-ctl org-list  # Should include 'lab' or configured organization name

# Key file verification
ls -la jtonello.pem  # Or configured username.pem
ls -la lab-validator.pem  # Or configured orgname-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443
curl -k https://localhost  # Should return Chef Automate login page

# Logs
sudo journalctl -u chef-automate -n 100
sudo chef-automate system-logs
sudo chef-server-ctl tail

# Service status
sudo systemctl status chef-automate
```