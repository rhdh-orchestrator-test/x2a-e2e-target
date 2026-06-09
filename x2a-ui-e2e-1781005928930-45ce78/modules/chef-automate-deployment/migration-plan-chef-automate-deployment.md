---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations. No actual Chef cookbook is present - just deployment scripts.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of bash scripts rather than Chef cookbooks. These scripts perform the following operations:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates an initial user with the configured username, email, and password
   - Creates an initial organization and associates the user with it
   - Generates PEM key files for the user and organization validator
   - Resources: bash commands, curl, chef-automate CLI, chef-server-ctl

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates an initial user with the configured username, email, and password
   - Creates an initial organization and associates the user with it
   - Generates PEM key files for the user and organization validator
   - Resources: bash commands, curl, chef-automate CLI, chef-server-ctl

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined, but requires sufficient system resources to run Chef Automate and Chef Infra Server

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (not a Chef cookbook with templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la ~/jtonello.pem
sudo chef-server-ctl org-list | grep lab
ls -la ~/lab-validator.pem

# Service connectivity
curl -k https://localhost/api/_status
curl -k https://localhost/organizations/lab

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
sudo chef-server-ctl tail

# Authentication test (using the created user)
knife user list -s https://localhost/organizations/lab -u jtonello -k ~/jtonello.pem

# System resources
free -m
df -h
top -n 1
```