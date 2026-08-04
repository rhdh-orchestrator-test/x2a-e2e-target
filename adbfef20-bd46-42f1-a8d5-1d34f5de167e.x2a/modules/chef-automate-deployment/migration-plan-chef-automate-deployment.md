---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl commands

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl commands

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

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# Key files
ls -la ~/${username}.pem
ls -la ~/${orgname}-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health
curl -k https://localhost/api/v0/health

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Chef server logs
sudo chef-server-ctl tail

# Disk usage
df -h /var/opt/chef-automate
df -h /var/opt/chef-server

# Memory usage
free -m
ps aux | grep chef | sort -nrk 4 | head -10
```