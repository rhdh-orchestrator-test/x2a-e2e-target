---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure Chef Automate and Chef Infra Server on a VM, create a user, and set up an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and extracts the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a user with the specified credentials
   - Creates an organization and associates the user with it
   - Saves user and organization validator keys to files
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and extracts the Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate) with the `--accept-terms-and-mlsa=true` flag
   - Creates a user with the specified credentials
   - Creates an organization and associates the user with it
   - Saves user and organization validator keys to files
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (Chef Automate handles its dependencies)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial admin user in Chef Automate/Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

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
sudo chef-server-ctl user-list | grep jtonello
ls -la jtonello.pem

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Web UI access
curl -k https://localhost/api/v0/health

# Service logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Chef Server logs
sudo chef-server-ctl tail

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/opscode

# Memory usage
free -m
ps aux | grep chef | sort -nrk 4 | head -10
```