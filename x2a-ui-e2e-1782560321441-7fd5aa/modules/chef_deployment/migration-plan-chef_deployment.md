---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef deployment toolkit consisting of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts configure system settings, download and install Chef components, and set up initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Platform (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Infra Server**: Deployed via deploy-automate.sh
  - Location/Path: Local system
  - Port/Socket: Default Chef Automate ports (443)
  - Key Config: User and organization creation

- **Chef Infra Server**: Deployed via deploy-chef-server.sh
  - Location/Path: Local system
  - Port/Socket: Default Chef Server ports (443)
  - Key Config: User and organization creation

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with MLSA acceptance
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server with MLSA acceptance
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for hostnamectl

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
- $userfilename (user PEM file)
- $orgfilename (organization validator PEM file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (if deploy-automate.sh was used)
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health
curl -k https://localhost/api/v0/health

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail
```