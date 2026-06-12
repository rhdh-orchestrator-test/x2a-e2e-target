---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Server

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Hostname: Configurable (default: automate.chef.lab)
  - Port/Socket: 443
  - Key Config: Accepts terms and MLSA, creates initial admin user and organization

- **Chef Infra Server (standalone)**:
  - Location/Path: Deployed on the local system
  - Hostname: Configurable (default: automate.chef.lab)
  - Port/Socket: 443
  - Key Config: Accepts terms and MLSA, creates initial admin user and organization

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates an initial user with:
     - Username: Configurable (default: jtonello)
     - Full name: Configurable (default: John Tonello)
     - Email: Configurable (default: jtonello@chef.lab)
     - Password: Configurable (default: password)
     - Saves user key to [username].pem
   - Creates an initial organization with:
     - Org short name: Configurable (default: lab)
     - Org full name: Configurable (default: Chef Lab)
     - Associates the created user with the organization
     - Saves organization validator key to [orgname]-validator.pem
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate deployment, user creation, organization creation

2. **deploy-chef-server.sh**:
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates an initial user with:
     - Username: Configurable (default: jtonello)
     - Full name: Configurable (default: John Tonello)
     - Email: Configurable (default: jtonello@chef.lab)
     - Password: Configurable (default: password)
     - Saves user key to [username].pem
   - Creates an initial organization with:
     - Org short name: Configurable (default: lab)
     - Org full name: Configurable (default: Chef Lab)
     - Associates the created user with the organization
     - Saves organization validator key to [orgname]-validator.pem
   - Resources: hostname configuration, sysctl parameters, file download, Chef Infra Server deployment, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- [username].pem (user key file)
- [orgname]-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# Hostname configuration
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Service status (for deploy-automate.sh)
sudo chef-automate status

# Service status (for deploy-chef-server.sh)
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost

# API access
curl -k https://localhost/organizations/lab
```