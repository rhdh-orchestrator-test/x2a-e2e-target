---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in deploy-automate.sh, standalone in deploy-chef-server.sh

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server with one command
   - Accepts terms and MLSA automatically
   - Resources: chef-automate deploy command with --product flags

4. **Product Deployment (Alternative)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server (without Automate)
   - Accepts terms and MLSA automatically
   - Resources: chef-automate deploy command with --product flag

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user in Chef Infra Server with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
   - Saves user key to a .pem file
   - Resources: chef-server-ctl user-create

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an organization in Chef Infra Server with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
   - Associates the previously created user with the organization
   - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Infra Server User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (default: jtonello.pem)
- Organization validator PEM file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no Chef templates used in these scripts)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname (default: automate.chef.lab)
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should exist and be executable
./chef-automate version  # Should show version information

# Service status
sudo systemctl status chef-automate  # Should be active
sudo systemctl status chef-server  # Should be active

# Web UI access
curl -k https://localhost/api/v0/health  # Should return health status for Chef Automate
curl -k https://localhost/organizations  # Should return organizations for Chef Infra Server

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user (default: jtonello)
sudo chef-server-ctl org-list  # Should include the created organization (default: lab)

# PEM files
ls -la jtonello.pem  # Should exist (or the configured username.pem)
ls -la lab-validator.pem  # Should exist (or the configured orgname-validator.pem)

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Logs
sudo journalctl -u chef-automate  # Check for errors
sudo journalctl -u chef-server  # Check for errors

# Network listening
sudo netstat -tulpn | grep 443  # Should show services listening on port 443
sudo ss -tlnp | grep 443  # Alternative check for services on port 443

# Authentication test (using the generated PEM file)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should succeed and list users
```