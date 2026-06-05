---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module contains shell scripts for deploying Chef Automate and Chef Infra Server. It configures a single instance of Chef infrastructure with user and organization setup.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:
- **Chef Automate with Infra Server**: A single instance of Chef Automate with integrated Chef Infra Server
  - Hostname: Configurable (default: automate.chef.lab)
  - Key Config: Includes user creation and organization setup

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters for Chef Automate:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate with Infra Server product bundle
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters for Chef Server:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server product (without Automate)
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

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

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Server/Automate

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/hostname (for hostname configuration)
- /etc/sysctl.conf or /etc/sysctl.d/* (for kernel parameter settings)
- Generated PEM files: [username].pem and [orgname]-validator.pem

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI/API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**: None (uses Chef Automate's built-in templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep [username]
sudo chef-server-ctl org-list | grep [orgname]

# PEM file verification
ls -la [username].pem
ls -la [orgname]-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/v0/status

# Service logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs
```