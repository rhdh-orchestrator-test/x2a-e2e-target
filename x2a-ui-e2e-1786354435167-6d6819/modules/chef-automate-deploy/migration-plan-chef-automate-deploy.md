---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in the main script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Resources: curl, gunzip, chmod, chef-automate (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user in Chef Infra Server with:
     - Username, full name, email, and password
     - Generates a user PEM file for API authentication
   - Creates an organization in Chef Infra Server with:
     - Organization short name and full name
     - Associates the created user with the organization
     - Generates an organization validator PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

4. **Chef Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Alternative script that follows the same steps as above but:
     - Only deploys Chef Infra Server without Automate
     - Uses the same user and organization setup process
   - Resources: Same as above but with different chef-automate deploy parameters

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
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial admin user in Chef Infra Server

### Authentication Keys

- **Variable(s)**: `userfilename`, `orgfilename`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated PEM files
- **Usage context**: Authentication keys for Chef Infra Server API access

## Checks for the Migration

**Files to verify**:
- Generated PEM files: `<username>.pem` and `<orgname>-validator.pem`
- Chef Automate configuration files (generated during deployment)
- Chef Infra Server configuration files (generated during deployment)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly in the scripts. Templates are handled internally by the Chef Automate deployment process.

## Pre-flight checks:

```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo systemctl status chef-automate
sudo systemctl status chef-server

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

# Web UI accessibility
curl -k https://localhost
curl -k https://localhost/_status

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate
sudo journalctl -u chef-server
sudo chef-automate logs

# API connectivity test (using the generated PEM file)
knife user list -s https://localhost/organizations/<orgname> -u <username> -k <username>.pem

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/opscode
```