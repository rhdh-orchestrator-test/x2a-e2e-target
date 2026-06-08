---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: 
  - Location/Path: Deployed on the same system as Chef Automate
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate, shares user and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment is performed through bash scripts rather than Chef recipes. The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for Chef Automate:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified credentials:
     - Username, full name, email, and password
     - Generates user PEM file
   - Creates an organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Generates organization validator PEM file
   - Resources: sysctl configurations (2), downloaded binaries (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Chef Automate
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for Chef Infra Server:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server with acceptance of terms
   - Creates a user with specified credentials:
     - Username, full name, email, and password
     - Generates user PEM file
   - Creates an organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Generates organization validator PEM file
   - Resources: sysctl configurations (2), downloaded binaries (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None (uses bash scripts)
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (bash scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/_status

# Chef Infra Server API access
knife user list -s https://localhost/organizations/lab -k ~/jtonello.pem -u jtonello

# Logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Health check
sudo chef-automate health check
sudo chef-server-ctl health-check
```