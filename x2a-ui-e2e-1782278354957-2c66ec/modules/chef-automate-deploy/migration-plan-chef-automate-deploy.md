---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of Bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
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
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Creates a Chef organization with the configured organization name
   - Associates the user with the organization
   - Generates and saves authentication key files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

4. **Alternative Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Similar to the main script but only deploys Chef Infra Server without Automate
   - Uses the same user and organization setup process
   - Resources: Same as main script but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None (standalone scripts)
**System package dependencies**: curl, gunzip, sudo
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
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`
- `/etc/chef/`
- Generated PEM files: `jtonello.pem`, `lab-validator.pem`

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Authentication key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://automate.chef.lab/api/v0/auth/version

# Chef Server API access
knife user list -s https://automate.chef.lab/organizations/lab -k jtonello.pem -u jtonello

# Logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Service health
sudo chef-automate service-versions
sudo chef-server-ctl service-list
```