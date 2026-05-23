---
source-path: setup-automate
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using shell scripts. It configures a single instance with user and organization setup. The main features include hostname configuration, system tuning, downloading and installing Chef Automate CLI, deploying Chef products, and creating initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: A combined deployment of Chef Automate and Chef Infra Server
  - Location/Path: Default installation path (managed by Chef Automate CLI)
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user creation, organization creation

- **Chef Infra Server**: A standalone deployment of Chef Infra Server
  - Location/Path: Default installation path (managed by Chef Automate CLI)
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user creation, organization creation

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM key files for user and organization
   - Resources: hostname configuration, sysctl, file download, command execution (5 resources)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM key files for user and organization
   - Resources: hostname configuration, sysctl, file download, command execution (5 resources)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip (part of gzip package)
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies managed by the installer

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: 
  - setup-automate/deploy-automate.sh
  - setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname change)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- Generated PEM files:
  - ${username}.pem (e.g., jtonello.pem)
  - ${orgname}-validator.pem (e.g., lab-validator.pem)
- Chef Automate configuration files (managed by Chef Automate)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
No templates are explicitly rendered in these scripts. The Chef Automate installer handles template rendering internally.

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# Kernel parameter verification
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI verification
ls -la ./chef-automate
./chef-automate version

# Service status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# System resources
free -m
df -h
```