---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: Deployed via deploy-automate.sh
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (Chef Automate UI), 80 (HTTP redirect)
  - Key Config: Hostname, user creation, organization creation

- **Chef Infra Server (standalone)**: Deployed via deploy-chef-server.sh
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (Chef Infra Server API), 80 (HTTP redirect)
  - Key Config: Hostname, user creation, organization creation

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization with the configured name and associates the user
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, user creation, organization creation

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization with the configured name and associates the user
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate and Chef Infra Server have their own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password
- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user authentication key)
- ~/${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI), 80 (HTTP redirect)
- Network interfaces: All interfaces by default

**Templates rendered**: None (shell scripts don't use templates)

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
ls -la ~/${username}.pem

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
ls -la ~/${orgname}-validator.pem

# Network listening
netstat -tulpn | grep -E ':443|:80'
ss -tlnp | grep -E ':443|:80'

# Service health
curl -k https://localhost/api/v0/health

# Logs
sudo journalctl -u chef-automate
sudo chef-automate logs

# For Chef Infra Server
sudo chef-server-ctl tail

# Disk usage
df -h /var/opt/chef-automate
df -h /var/opt/opscode

# Memory usage
free -m
ps aux | grep chef | sort -k 4 -r | head -10
```