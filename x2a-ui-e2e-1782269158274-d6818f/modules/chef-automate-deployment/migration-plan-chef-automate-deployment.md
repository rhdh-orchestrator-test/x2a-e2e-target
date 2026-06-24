---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup, system tuning, and deployment of Chef products.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system alongside Chef Automate
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
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
     - Username, full name, email, and password
     - Generates user key file (e.g., 'jtonello.pem')
   - Creates a Chef organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Generates organization validator key file (e.g., 'lab-validator.pem')
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

The `setup-automate/deploy-chef-server.sh` script follows a similar pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (uses bash scripts)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

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
- **Usage context**: Used to create the initial Chef user account for authentication to Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `/etc/opscode/` (Chef Infra Server configuration directory)
- User key file (e.g., `jtonello.pem`)
- Organization validator key file (e.g., `lab-validator.pem`)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
- No templates are explicitly rendered in the scripts

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Service status
sudo chef-automate status  # Check Chef Automate services
sudo chef-server-ctl status  # Check Chef Infra Server services

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# Key files
ls -la jtonello.pem  # Verify user key exists (adjust filename as needed)
ls -la lab-validator.pem  # Verify org validator key exists (adjust filename as needed)

# Web UI and API access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/_status  # Should return Chef Infra Server status

# Network listening
sudo netstat -tulpn | grep 443  # Verify HTTPS port is listening
sudo ss -tlnp | grep 443  # Alternative to netstat

# Logs
sudo chef-automate logs  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs

# Authentication test (requires the user key file)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should list users without errors

# Organization validation (requires the validator key)
knife client list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should include the validator client
```