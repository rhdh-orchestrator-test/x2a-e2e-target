---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup. The scripts handle system prerequisites, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

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
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of bash scripts that perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username, full name, email, password
     - Saves user key to a .pem file
   - Creates a Chef organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip (part of gzip package)
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
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial Chef administrator user

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `$userfilename` (User key file, e.g., jtonello.pem)
- `$orgfilename` (Organization validator key, e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
- No templates are explicitly rendered by the scripts (Chef Automate handles its own templating)

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
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
sudo chef-server-ctl org-show lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Web UI access
curl -k https://localhost/api/v0/status
curl -k https://localhost/_status

# Authentication test
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Logs
sudo journalctl -u chef-automate
sudo chef-automate logs

# Service health
sudo chef-automate service-versions
sudo chef-automate config show
```