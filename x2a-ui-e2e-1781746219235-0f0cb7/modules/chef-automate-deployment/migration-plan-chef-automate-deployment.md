---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server product

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl to the configured hostname value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username, full name, email, and password
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The `setup-automate/deploy-chef-server.sh` script follows a similar pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef-automate/
- User PEM file (jtonello.pem in the example)
- Organization validator PEM file (lab-validator.pem in the example)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost

# Chef Server API access
curl -k https://localhost/organizations
knife ssl check -s https://localhost/organizations/lab

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la jtonello.pem
knife user list -s https://localhost/organizations/lab -k jtonello.pem -u jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem
knife client list -s https://localhost/organizations/lab -k lab-validator.pem -u lab-validator

# Logs
sudo chef-automate logs
sudo chef-server-ctl tail
journalctl -u chef-automate
journalctl -u chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Resource usage
df -h
free -m
top -n 1 | grep chef
```