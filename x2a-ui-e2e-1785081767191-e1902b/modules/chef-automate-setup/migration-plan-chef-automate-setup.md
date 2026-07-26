---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-setup

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the products, and create a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in one script, standalone in the other

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to a configurable value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a user with configurable parameters:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates an organization with configurable parameters:
     - Org short name: lab (configurable)
     - Org full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Saves organization validator key to lab-validator.pem
   - Resources: hostname configuration, sysctl parameters, file download, command execution

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to a configurable value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a user with configurable parameters (same as above)
   - Creates an organization with configurable parameters (same as above)
   - Resources: hostname configuration, sysctl parameters, file download, command execution

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

### User Password
- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef Infra Server admin user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- Generated PEM files: jtonello.pem, lab-validator.pem (or as configured)
- Chef Automate CLI binary: ./chef-automate

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: No templates are used in these scripts.

## Pre-flight checks:
```bash
# Hostname configuration
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la chef-automate
./chef-automate version

# Chef Automate status
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/v0/health

# Chef Automate UI access
curl -k -I https://localhost

# Log verification
sudo journalctl -u chef-automate
```