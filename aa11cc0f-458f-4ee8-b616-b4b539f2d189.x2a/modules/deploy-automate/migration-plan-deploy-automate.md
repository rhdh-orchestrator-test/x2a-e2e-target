---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: deploy-automate

**TLDR**: This is a simple bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Organization name, user association

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **Set hostname** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Resources: hostnamectl command (1)

2. **Configure system parameters** (`setup-automate/deploy-automate.sh`):
   - Sets vm.max_map_count=262144 for Elasticsearch
   - Sets vm.dirty_expire_centisecs=20000 for disk performance
   - Resources: sysctl command (2)

3. **Download Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads the Chef Automate CLI from packages.chef.io
   - Extracts and makes it executable
   - Resources: curl, gunzip, chmod commands (3)

4. **Deploy Chef Automate and Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs the Chef Automate deployment with both products
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command (1)

5. **Create user** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the specified credentials
   - Saves the user's private key to a .pem file
   - Resources: chef-server-ctl user-create command (1)

6. **Create organization** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef organization
   - Associates the previously created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl org-create command (1)

## Dependencies

**External cookbook dependencies**: None (this is a standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `chef-automate` executable in the directory where the script was run
- User PEM file (e.g., `jtonello.pem`) in the directory where the script was run
- Organization validator PEM file (e.g., `lab-validator.pem`) in the directory where the script was run

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files existence
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Network listening
ss -tlnp | grep ':443'
netstat -tulpn | grep ':443'

# Service logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Chef server API test (using the created PEM file)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem
```