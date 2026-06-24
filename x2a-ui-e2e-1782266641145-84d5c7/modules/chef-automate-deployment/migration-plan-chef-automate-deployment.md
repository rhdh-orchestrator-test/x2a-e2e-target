---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the combined deployment script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads the Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Resources: curl, chmod (2)

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

4. **Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

5. **User and Organization Setup** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an initial user with the configured parameters:
     - Username: jtonello
     - Full name: John Tonello
     - Email: jtonello@chef.lab
     - Password: password
     - Saves user key to jtonello.pem
   - Creates an initial organization with the configured parameters:
     - Organization short name: lab
     - Organization full name: Chef Lab
     - Associates the created user with the organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but requires systemd for service management

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
- **Usage context**: Used for creating the initial Chef Infra Server admin user

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef-automate/
- Generated PEM files: jtonello.pem, lab-validator.pem

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (bash scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should return automate.chef.lab
sysctl vm.max_map_count  # Should return vm.max_map_count = 262144
sysctl vm.dirty_expire_centisecs  # Should return vm.dirty_expire_centisecs = 20000

# Chef Automate CLI
ls -la chef-automate  # Should show executable permissions
./chef-automate version  # Should return version information

# Service status
sudo systemctl status chef-automate  # Should be active
sudo systemctl status chef-server  # Should be active

# Web UI accessibility
curl -k https://localhost/api/v0/health  # Should return health status for Chef Automate
curl -k https://localhost/organizations  # Should return organizations for Chef Infra Server

# User and organization verification
sudo chef-server-ctl user-list  # Should include jtonello
sudo chef-server-ctl org-list  # Should include lab

# PEM files
ls -la jtonello.pem  # Should exist and be readable
ls -la lab-validator.pem  # Should exist and be readable

# Network listening
sudo netstat -tulpn | grep 443  # Should show services listening on port 443
sudo ss -tlnp | grep 443  # Alternative check for services on port 443

# Logs
sudo journalctl -u chef-automate -n 50  # Check Chef Automate logs
sudo journalctl -u chef-server -n 50  # Check Chef Infra Server logs

# API accessibility (requires the PEM file)
knife user list -s https://localhost -u jtonello -k jtonello.pem  # Should list users
knife org list -s https://localhost -u jtonello -k jtonello.pem  # Should list organizations
```