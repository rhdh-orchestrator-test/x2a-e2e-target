---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a Bash script that deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (typically 443)
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
   - Deploys Chef Automate with Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial user with chef-server-ctl:
     - Username: configured value (default: 'jtonello')
     - Full name: configured value (default: 'John Tonello')
     - Email: configured value (default: 'jtonello@chef.lab')
     - Password: configured value (default: 'password')
     - Saves user key to file: username.pem
   - Creates initial organization with chef-server-ctl:
     - Org short name: configured value (default: 'lab')
     - Org full name: configured value (default: 'Chef Lab')
     - Associates with created user
     - Saves org validator key to file: orgname-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

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

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (default: jtonello.pem)
- Organization validator PEM file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should return 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should return 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/health

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl test

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username (default: jtonello)
sudo chef-server-ctl org-list  # Should include the configured org name (default: lab)

# PEM files verification
ls -la jtonello.pem  # Should exist and have proper permissions
ls -la lab-validator.pem  # Should exist and have proper permissions

# Network listening
sudo netstat -tulpn | grep LISTEN  # Should show Chef Automate and Chef Infra Server ports
sudo ss -tulpn | grep LISTEN  # Alternative to netstat

# Service status
sudo systemctl status chef-automate

# Logs
sudo journalctl -u chef-automate -f
sudo chef-automate system-logs
```