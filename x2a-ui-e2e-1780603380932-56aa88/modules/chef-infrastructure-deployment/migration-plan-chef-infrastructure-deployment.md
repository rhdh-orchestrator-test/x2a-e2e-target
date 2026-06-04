---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts for deploying Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:

- **Chef Automate Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default Chef Automate ports (443)
  - Key Config: Hostname, user creation, organization setup

- **Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default Chef Server ports (443)
  - Key Config: Hostname, user creation, organization setup

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two shell scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and prepares Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--product automate --product infra-server`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the created user with it
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, user creation, organization creation

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads and prepares Chef Automate CLI
   - Deploys only Chef Infra Server with `--product infra-server`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the created user with it
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate and Chef Infra Server have their own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `chef-automate` executable in the directory where the script was run
- User PEM file (e.g., `jtonello.pem`) in the directory where the script was run
- Organization validator PEM file (e.g., `lab-validator.pem`) in the directory where the script was run

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly in the scripts, but Chef Automate and Chef Infra Server will create their own configuration files

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la chef-automate
./chef-automate version

# Chef Automate status (if deployed with automate)
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User and organization verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Chef Server API access test
knife user list -s https://localhost/organizations/lab -u jtonello --key jtonello.pem

# Web UI access
curl -k https://localhost/api/_status

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Log verification
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Chef Server component status
sudo chef-server-ctl status
```