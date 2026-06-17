---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a single instance of Chef Automate with integrated Chef Infra Server, configures system parameters, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Single instance deployment with integrated Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: System parameters (vm.max_map_count=262144, vm.dirty_expire_centisecs=20000)

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with integrated Chef Infra Server
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
     - Username, full name, email, and password are configurable
     - Saves user key to a PEM file
   - Creates initial organization
     - Organization short name and full name are configurable
     - Associates the admin user with the organization
     - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `${username}.pem` (user key file in the current directory)
- `${orgname}-validator.pem` (organization validator key in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

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

# User verification
sudo chef-server-ctl user-list | grep $(grep username setup-automate/deploy-automate.sh | head -1 | cut -d "'" -f 2)

# Organization verification
sudo chef-server-ctl org-list | grep $(grep orgname setup-automate/deploy-automate.sh | head -1 | cut -d "'" -f 2)

# Key files
ls -la $(grep username setup-automate/deploy-automate.sh | head -1 | cut -d "'" -f 2).pem
ls -la $(grep orgname setup-automate/deploy-automate.sh | head -1 | cut -d "'" -f 2)-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 50
```