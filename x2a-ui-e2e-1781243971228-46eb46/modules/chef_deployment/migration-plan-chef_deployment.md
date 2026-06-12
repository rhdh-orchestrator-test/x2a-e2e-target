---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in one script, standalone in the other

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a Chef user with the configured username, name, email, and password
   - Creates a Chef organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a Chef user with the configured username, name, email, and password
   - Creates a Chef organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for hostname setting

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- $userfilename (user PEM file created by chef-server-ctl)
- $orgfilename (organization validator PEM file created by chef-server-ctl)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Unix sockets: None explicitly defined
- Network interfaces: Default (all interfaces)

**Templates rendered**:
None (no Chef templates used in these scripts)

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

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# PEM files existence
ls -la $userfilename
ls -la $orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI accessibility
curl -k https://localhost

# Chef server API accessibility
knife user list -s https://localhost/organizations/$orgname -u $username -k $userfilename

# Log verification
sudo journalctl -u chef-automate
sudo journalctl -u chef-server
```