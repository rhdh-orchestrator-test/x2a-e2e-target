---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Automate, configured with initial user and organization

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

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate with Infra Server integration
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial user with specified credentials:
     - Username, full name, email, and password
     - Saves user key to a .pem file
   - Creates organization with specified details:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

The `setup-automate/deploy-chef-server.sh` script follows a similar pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script-based deployment)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate and Chef Infra Server status
sudo chef-automate status
curl -k https://localhost/api/v0/health

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# Key files
ls -la ~/$userfilename
ls -la ~/$orgfilename

# Service status
sudo systemctl status chef-automate
sudo chef-server-ctl status

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
```