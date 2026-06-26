---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Server

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default Chef Automate ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server (standalone)**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default Chef Server ports (443 for web UI)
  - Key Config: Configured with user and organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform the following operations:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM files for the user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM files for the user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on Chef Automate CLI to handle dependencies)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameter verification
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI verification
ls -la ./chef-automate
./chef-automate version

# Service status (for Chef Automate with Infra Server)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://automate.chef.lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-automate logs
sudo chef-server-ctl tail
```