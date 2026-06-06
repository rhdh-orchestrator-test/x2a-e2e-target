---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of bash scripts that deploy Chef Automate and Chef Infra Server:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

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
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`: Chef Server configuration directory
- `/etc/chef/`: Chef client configuration directory
- User and organization PEM files in the current directory:
  - `jtonello.pem` (or the configured username)
  - `lab-validator.pem` (or the configured organization name)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are explicitly rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify Chef Automate UI is accessible
curl -k https://localhost/api/v0/auth/version

# Verify Chef Infra Server API is accessible
curl -k https://localhost/organizations

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Verify user PEM file exists and is valid
[ -f jtonello.pem ] && echo "User PEM file exists" || echo "User PEM file missing"
openssl rsa -in jtonello.pem -check -noout

# Verify organization validator PEM file exists and is valid
[ -f lab-validator.pem ] && echo "Organization validator PEM file exists" || echo "Organization validator PEM file missing"
openssl rsa -in lab-validator.pem -check -noout

# Check Chef Automate services
sudo systemctl status chef-automate

# Check Chef Server services
sudo systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Test API access with the created user
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem
```