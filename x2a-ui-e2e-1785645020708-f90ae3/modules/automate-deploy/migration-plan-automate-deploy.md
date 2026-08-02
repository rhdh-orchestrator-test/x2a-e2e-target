---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deploy

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup, system tuning, and deployment of Chef products.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the same deployment

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username, full name, email, password
     - Generates and saves user key file
   - Creates a Chef organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Generates and saves organization validator key file
   - Resources: chef-server-ctl commands (2)

The alternative script (`setup-automate/deploy-chef-server.sh`) performs similar operations but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined (Chef Automate manages its own services)

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Automate/Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`: Configuration directory for Chef Infra Server
- `/etc/chef/`: Configuration directory for Chef clients
- User key file: `<username>.pem` (in the current directory)
- Organization validator key file: `<orgname>-validator.pem` (in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
- No templates are explicitly rendered by these scripts (Chef Automate handles its own templating internally)

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
sudo chef-server-ctl user-show <username>

# Organization verification
sudo chef-server-ctl org-list | grep <orgname>
sudo chef-server-ctl org-show <orgname>

# Key files
ls -la <username>.pem
ls -la <orgname>-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Logs
sudo journalctl -u chef-automate
sudo chef-automate logs

# Service status
sudo systemctl status chef-automate
```