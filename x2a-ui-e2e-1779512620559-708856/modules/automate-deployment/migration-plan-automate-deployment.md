---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using bash scripts. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value using hostnamectl
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl command, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with chef-server-ctl
     - Username, full name, email, and password are configurable
     - Saves user key to a .pem file
   - Creates initial organization with chef-server-ctl
     - Organization short name and full name are configurable
     - Associates the admin user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

The `setup-automate/deploy-chef-server.sh` script follows a similar pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `chef-automate` executable in the directory where the script was run
- User key file (e.g., `jtonello.pem`)
- Organization validator key file (e.g., `lab-validator.pem`)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Verify key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Check Chef Automate UI accessibility
curl -k https://localhost/api/v0/auth/version

# Check Chef Infra Server API accessibility
curl -k https://localhost/organizations/lab

# Verify services are running
sudo systemctl status chef-automate
sudo chef-server-ctl service-list

# Check logs
sudo chef-automate system-logs

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Resource usage
df -h
free -m
top -n 1
```