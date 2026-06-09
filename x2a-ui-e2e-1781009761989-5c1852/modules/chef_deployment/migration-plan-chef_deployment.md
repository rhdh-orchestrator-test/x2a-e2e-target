---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure Chef Automate and Chef Infra Server on a Linux system. The scripts set up hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create a user and organization.

## Service Type and Instances

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate and Infra Server**: A single instance of Chef Automate with Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Chef Automate web UI)
  - Key Config: User and organization creation with authentication keys

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The setup-automate module performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with accepted terms
   - Creates a Chef user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates a Chef organization:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Saves organization validator key to lab-validator.pem
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, Chef Automate CLI, Chef server commands

2. **deploy-chef-server.sh**:
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server with accepted terms
   - Creates a Chef user with specified credentials (same as above)
   - Creates a Chef organization (same as above)
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, Chef Automate CLI, Chef server commands

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

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User key file (jtonello.pem by default)
- Organization validator key file (lab-validator.pem by default)
- Chef Automate configuration files (typically in /etc/chef-automate/)
- Chef Server configuration files (typically in /etc/opscode/)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI), 80 (HTTP redirect to HTTPS)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

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

# Chef Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files existence
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Web UI accessibility
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# Chef Server API accessibility
curl -k https://localhost/organizations/lab

# Service status
systemctl status chef-automate
journalctl -u chef-automate -f

# Logs
sudo chef-automate logs
tail -f /var/log/chef-server/nginx/access.log
tail -f /var/log/chef-server/nginx/error.log

# Disk space
df -h /var/opt/chef-automate/
df -h /var/opt/opscode/

# Memory usage
free -m
```