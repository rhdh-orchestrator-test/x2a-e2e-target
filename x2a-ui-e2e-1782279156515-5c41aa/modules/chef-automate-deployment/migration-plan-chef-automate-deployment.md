---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: Combined deployment of Chef Automate and Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Custom hostname, user creation, organization creation

- **Chef Infra Server**: Standalone deployment of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Custom hostname, user creation, organization creation

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: sysctl (2), curl (1), chmod (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: sysctl (2), curl (1), chmod (1), chef-automate deploy (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: bash, curl, sudo, hostnamectl (systemd-services)
**Service dependencies**: None explicitly defined (Chef Automate manages its own services)

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
- **Usage context**: This credential is used as the password for the initial admin user created in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/hostname
- /etc/chef-server (Chef Server configuration directory)
- /var/opt/chef-server (Chef Server data directory)
- /var/log/chef-server (Chef Server logs)
- Generated PEM files: `<username>.pem` and `<orgname>-validator.pem` in the current directory

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
cat /etc/hosts | grep $(hostname)
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# Verify admin user and organization
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Verify PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test API access
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Service logs
sudo journalctl -u chef-automate -n 50
sudo tail -n 50 /var/log/chef-server/nginx/access.log
sudo tail -n 50 /var/log/chef-server/nginx/error.log

# Web UI access
curl -k https://localhost/api/v0/health

# Memory usage
free -m
ps aux | grep chef | sort -k 4 -r | head -10
```