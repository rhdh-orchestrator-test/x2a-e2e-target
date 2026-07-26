---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of Bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and execute the Chef Automate CLI, and configure initial users and organizations. No actual Chef cookbook is present - these are deployment scripts for Chef's own infrastructure components.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization name

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Hostname, user credentials, organization name

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of Bash scripts rather than Chef cookbooks. These scripts deploy Chef's own infrastructure components:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate CLI, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate CLI, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: curl, sudo, hostnamectl (systemd)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Admin User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used as the email address for the initial admin user

### User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the admin user

### Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the organization

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (admin user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None (not a Chef cookbook with templates)

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

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
```