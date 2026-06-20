---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef_automate_deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Default installation path
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
   - Sets hostname to the configured value using hostnamectl
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified username, name, email, and password
   - Saves user key to a PEM file
   - Creates a Chef organization with specified name
   - Associates the user with the organization
   - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

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
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `chef-automate` executable in the directory where the script was run
- User PEM file (e.g., `jtonello.pem`)
- Organization validator PEM file (e.g., `lab-validator.pem`)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Chef server API accessibility
knife user list -s https://localhost/organizations/lab -k jtonello.pem -u jtonello

# Logs
sudo chef-automate logs

# Service status
systemctl list-units | grep chef
systemctl status chef-automate

# Disk space
df -h
```