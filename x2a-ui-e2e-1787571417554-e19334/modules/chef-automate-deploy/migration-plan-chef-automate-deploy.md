---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the value specified in the hostname variable
   - Configures kernel parameters:
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
     - Username: Variable-defined (default: jtonello)
     - Full name: Variable-defined (default: John Tonello)
     - Email: Variable-defined (default: jtonello@chef.lab)
     - Password: Variable-defined (default: password)
     - Saves user key to [username].pem file
   - Creates a Chef organization:
     - Short name: Variable-defined (default: lab)
     - Full name: Variable-defined (default: Chef Lab)
     - Associates with the created user
     - Saves organization validator key to [orgname]-validator.pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, hostnamectl, sysctl
**Service dependencies**: None explicitly defined, but Chef Automate has its own service dependencies

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword` (default value: 'password')
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded in script
- **Usage context**: Used to create the initial Chef user account with chef-server-ctl user-create command

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/hostname (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- ./chef-automate (downloaded binary)
- ./[username].pem (generated user key file)
- ./[orgname]-validator.pem (generated organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo ./chef-automate status
curl -k https://localhost/api/v0/health

# Chef Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ./jtonello.pem
ls -la ./lab-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service logs
sudo ./chef-automate system-logs
journalctl -u chef-automate
journalctl -u chef-server

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/v0/version
```