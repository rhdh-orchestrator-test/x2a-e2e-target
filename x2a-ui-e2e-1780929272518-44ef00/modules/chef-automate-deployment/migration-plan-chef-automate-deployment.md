---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up a Chef server with a single admin user and organization. The deployment is straightforward with minimal configuration options.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization name

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization name

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with default settings
   - Creates an admin user with specified credentials
   - Creates an organization and associates the admin user with it
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with default settings
   - Creates an admin user with specified credentials
   - Creates an organization and associates the admin user with it
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

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
- **Usage context**: Used for creating the initial admin user in Chef Automate/Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `chef-automate` executable in the directory where the script was run
- User PEM file (e.g., `jtonello.pem`) in the directory where the script was run
- Organization validator PEM file (e.g., `lab-validator.pem`) in the directory where the script was run

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment uses default templates from the Chef Automate package)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la chef-automate
./chef-automate version

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# User and organization verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://automate.chef.lab/_status
curl -k https://automate.chef.lab/api/v0/auth/version

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Log files
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Chef server API check (using the created admin user)
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem --ssl-verify=false

# Chef organization check
knife org list -s https://automate.chef.lab -u jtonello -k jtonello.pem --ssl-verify=false

# Chef Automate API health check
curl -k https://automate.chef.lab/api/v0/health

# Disk space check
df -h /var
```