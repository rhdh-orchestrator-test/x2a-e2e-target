---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl command, file permissions change

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flags

4. **Chef Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a Chef user with the configured details:
     - Username, full name, email, and password
     - Saves user key to a .pem file
   - Creates a Chef organization with the configured details:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for hostname configuration

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: This credential is used to set the password for the initial Chef user created during deployment

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ./jtonello.pem
ls -la ./lab-validator.pem

# Service status
curl -k https://localhost/api/v0/health
curl -k https://localhost/organizations/lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
```