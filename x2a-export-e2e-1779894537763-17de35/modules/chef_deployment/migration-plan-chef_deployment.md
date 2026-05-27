---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with accepted terms
   - Creates a user with specified details:
     - Username, full name, email, and password
     - Saves user key to a .pem file
   - Creates an organization with specified details:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate) with accepted terms
   - Creates a user with specified details:
     - Username, full name, email, and password
     - Saves user key to a .pem file
   - Creates an organization with specified details:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for hostname setting

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: 
  - setup-automate/deploy-automate.sh
  - setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Unix sockets: None specified
- Network interfaces: Default (0.0.0.0)

**Templates rendered**:
No templates are explicitly rendered in these scripts.

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameter verification
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI verification
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username
ls -la $userfilename

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
ls -la $orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
systemctl status chef-server

# Web UI access
curl -k https://localhost

# API access
curl -k https://localhost/organizations/$orgname
```