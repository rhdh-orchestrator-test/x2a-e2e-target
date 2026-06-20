---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that set up either Chef Automate with Chef Infra Server or just Chef Infra Server alone on a VM, configuring hostname, system parameters, downloading the Chef Automate CLI, deploying the selected products, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Key Config: Accepts terms and MLSA, creates user and organization

- **Chef Infra Server (standalone)**:
  - Location/Path: Deployed on the local system
  - Key Config: Accepts terms and MLSA, creates user and organization

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The setup-automate module performs operations in this order:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with acceptance of terms
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user and organization
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
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
- **Usage context**: Used for creating the initial Chef user

## Checks for the Migration

**Files to verify**:
- User PEM file: `<username>.pem` (default: jtonello.pem)
- Organization validator PEM file: `<orgname>-validator.pem` (default: lab-validator.pem)

**Service endpoints to check**:
- Chef Automate UI (typically https://hostname)
- Chef Infra Server API (typically https://hostname/organizations/orgname)

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

# User verification
sudo chef-server-ctl user-list | grep <username>

# Organization verification
sudo chef-server-ctl org-list | grep <orgname>

# PEM file verification
ls -la <username>.pem
ls -la <orgname>-validator.pem

# API connectivity test
knife ssl check -s https://$(hostname) -u <username> -k <username>.pem -o <orgname>

# Web UI access
curl -k -I https://$(hostname)

# Service processes
ps aux | grep chef

# Logs
sudo journalctl -u chef-automate
sudo chef-automate logs

# Network listening
sudo netstat -tulpn | grep -E '443|80'
sudo ss -tlnp | grep -E '443|80'
```