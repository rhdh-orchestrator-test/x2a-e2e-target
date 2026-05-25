---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef Automate and Chef Infra Server deployment module consisting of two bash scripts. The scripts deploy either Chef Automate with Chef Infra Server or just Chef Infra Server alone, create an initial admin user, and set up an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: Deploys both Chef Automate and Chef Infra Server on a single VM
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (Chef Automate: 443, Chef Server: 443)
  - Key Config: Creates admin user and organization

- **Chef Infra Server**: Deploys only Chef Infra Server without Chef Automate
  - Location/Path: Installed on the local system
  - Port/Socket: Default port (443)
  - Key Config: Creates admin user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates an admin user with specified credentials
   - Creates an organization and associates the admin user
   - Resources: hostname configuration, sysctl settings, file download, command execution

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server with acceptance of terms
   - Creates an admin user with specified credentials
   - Creates an organization and associates the admin user
   - Resources: hostname configuration, sysctl settings, file download, command execution

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
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`: Chef Server configuration directory
- `/etc/chef-automate/`: Chef Automate configuration directory
- `chef-automate`: Downloaded CLI tool
- `$userfilename` (e.g., jtonello.pem): Admin user key file
- `$orgfilename` (e.g., lab-validator.pem): Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for both Chef Automate and Chef Infra Server)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are used in this cookbook.

## Pre-flight checks:
```bash
# System hostname check
hostname
hostnamectl status | grep "Static hostname"

# Kernel parameter checks
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI tool check
ls -la ./chef-automate
./chef-automate version

# Service status checks
sudo chef-automate status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# File existence checks
ls -la $userfilename
ls -la $orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web interface accessibility
curl -k https://localhost/api/v0/health

# Chef Server API check
knife user list -s https://localhost/organizations/$orgname -u $username -k $userfilename --no-editor

# Log checks
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Configuration validation
sudo chef-automate config show
```