---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Setup

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Infra Server products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central server for Chef automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed alongside Chef Automate
  - Port/Socket: Default ports (443)
  - Key Config: Configured with user and organization

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The bash script performs operations in this order:

1. **Set hostname** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the value specified in the hostname variable
   - Resources: hostnamectl command

2. **Configure system parameters** (`setup-automate/deploy-automate.sh`):
   - Sets vm.max_map_count=262144
   - Sets vm.dirty_expire_centisecs=20000
   - Resources: sysctl command (2)

3. **Download and install Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes it executable
   - Resources: curl, gunzip, chmod commands

4. **Deploy Chef Automate and Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs chef-automate deploy command
   - Installs both automate and infra-server products
   - Accepts terms and MLSA
   - Resources: chef-automate command

5. **Create Chef user** (`setup-automate/deploy-automate.sh`):
   - Creates a user with specified username, full name, email, and password
   - Saves user key to a .pem file
   - Resources: chef-server-ctl user-create command

6. **Create Chef organization** (`setup-automate/deploy-automate.sh`):
   - Creates an organization with specified short name and full name
   - Associates the previously created user with the organization
   - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None (this is a bash script, not a Chef cookbook)
**System package dependencies**: curl, gunzip, chmod (for downloading and preparing Chef Automate CLI)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname change)
- /proc/sys/vm/max_map_count (for sysctl parameter)
- /proc/sys/vm/dirty_expire_centisecs (for sysctl parameter)
- chef-automate executable in current directory
- User PEM file (jtonello.pem by default)
- Organization validator PEM file (lab-validator.pem by default)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (this is a bash script, not a Chef cookbook with templates)

## Pre-flight checks:
```bash
# Hostname check
hostname
hostnamectl

# System parameters check
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI check
ls -la chef-automate
./chef-automate version

# Chef Automate status
sudo ./chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files check
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://automate.chef.lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
```