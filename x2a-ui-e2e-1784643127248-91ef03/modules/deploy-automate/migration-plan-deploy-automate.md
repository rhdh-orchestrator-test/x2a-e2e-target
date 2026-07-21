---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: deploy-automate

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the services, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Main automation platform for Chef
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **Set hostname** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Resources: hostnamectl command (1)

2. **Configure system parameters** (`setup-automate/deploy-automate.sh`):
   - Sets vm.max_map_count=262144 for Elasticsearch
   - Sets vm.dirty_expire_centisecs=20000 for disk I/O optimization
   - Resources: sysctl command (2)

3. **Download Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads the latest Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands (3)

4. **Deploy Chef Automate and Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs the Chef Automate deployment with both products
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command (1)

5. **Create user** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Saves the user key to a .pem file
   - Resources: chef-server-ctl user-create command (1)

6. **Create organization** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef organization with the configured name
   - Associates the previously created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl org-create command (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

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
- `/etc/hostname` (should contain the configured hostname)
- `${username}.pem` (user key file in the current directory)
- `${orgname}-validator.pem` (organization validator key in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None explicitly rendered by the script. The Chef Automate deployment process handles its own templating.

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Service status
sudo systemctl status chef-automate
curl -k https://localhost/api/v0/status

# Chef Infra Server status
sudo chef-server-ctl status
curl -k https://localhost/organizations

# User and organization verification
ls -la ./${username}.pem
ls -la ./${orgname}-validator.pem

# Test user authentication
knife user list -s https://localhost -u ${username} -k ./${username}.pem

# Test organization access
knife org list -s https://localhost -u ${username} -k ./${username}.pem

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Logs
sudo journalctl -u chef-automate -n 100
sudo chef-automate system-logs
```