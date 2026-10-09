---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is not a Chef cookbook but a collection of shell scripts that deploy Chef Automate and Chef Infra Server infrastructure. It contains two deployment scripts that install and configure Chef infrastructure components with basic user and organization setup.

## Service Type and Instances

**Service Type**: Infrastructure Management Platform

**Configured Instances**:
- **Chef Automate + Infra Server**: Combined deployment
  - Location/Path: deploy-automate.sh
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname automate.chef.lab, user jtonello, organization lab

- **Chef Infra Server Only**: Standalone deployment
  - Location/Path: deploy-chef-server.sh
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname automate.chef.lab, user jtonello, organization lab

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The setup performs operations in this order:

1. **deploy-automate.sh** (`deploy-automate.sh`):
   - Step 1: Sets system hostname to 'automate.chef.lab'
   - Step 2: Configures kernel parameters vm.max_map_count=262144, vm.dirty_expire_centisecs=20000
   - Step 3: Downloads chef-automate CLI tool from packages.chef.io
   - Step 4: Deploys both Chef Automate and Chef Infra Server with auto-acceptance of terms
   - Step 5: Creates Chef user 'jtonello' with password authentication
   - Step 6: Creates Chef organization 'lab' with association to user 'jtonello'
   - Step 7: Generates PEM files jtonello.pem and lab-validator.pem

2. **deploy-chef-server.sh** (`deploy-chef-server.sh`):
   - Step 1: Sets system hostname to 'automate.chef.lab'
   - Step 2: Configures kernel parameters vm.max_map_count=262144, vm.dirty_expire_centisecs=20000
   - Step 3: Downloads chef-automate CLI tool from packages.chef.io
   - Step 4: Deploys only Chef Infra Server without Automate with auto-acceptance of terms
   - Step 5: Creates Chef user 'jtonello' with password authentication
   - Step 6: Creates Chef organization 'lab' with association to user 'jtonello'
   - Step 7: Generates PEM files jtonello.pem and lab-validator.pem

## Dependencies

**External cookbook dependencies**: None (shell scripts only)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: Internet connectivity to packages.chef.io, systemd

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None
  - **Path**: None

### User Password
- **Variable(s)**: userpassword='password'
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Chef user account password for initial setup

### User Email
- **Variable(s)**: useremail='jtonello@chef.lab'
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Chef user account email address

### Generated PEM Files
- **Variable(s)**: userfilename="${username}.pem", orgfilename="${orgname}-validator.pem"
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: generated files
- **Usage context**: Chef authentication keys for user and organization validator

## Checks for the Migration

**Files to verify**: deploy-automate.sh, deploy-chef-server.sh, jtonello.pem, lab-validator.pem
**Service endpoints to check**: 443 (HTTPS)
**Templates rendered**: No templates (shell scripts only)

## Pre-flight checks:
```bash
# System hostname verification for Chef Automate + Infra Server instance
hostname
hostnamectl status | grep "Static hostname"

# System hostname verification for Chef Infra Server Only instance
hostname
hostnamectl status | grep "Static hostname"

# Kernel parameter verification for Chef Automate + Infra Server instance
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Kernel parameter verification for Chef Infra Server Only instance
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate service status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Web interface accessibility
curl -k -I https://automate.chef.lab
curl -k -I https://automate.chef.lab/organizations/lab

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab
sudo chef-server-ctl org-show lab

# PEM file verification
ls -la jtonello.pem lab-validator.pem
file jtonello.pem lab-validator.pem

# Network listening verification
netstat -tulpn | grep :443
ss -tlnp | grep :443
lsof -i :443

# System resources
df -h
free -h
ps aux | grep -E "(chef|automate)"
```