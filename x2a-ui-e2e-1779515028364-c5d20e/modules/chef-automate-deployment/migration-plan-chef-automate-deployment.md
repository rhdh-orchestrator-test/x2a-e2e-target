---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and configure initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: 443 (HTTPS for Chef Automate UI and API)
  - Key Config: Accepts terms and MLSA agreement
  
- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: 443 (shared with Chef Automate)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Creates a Chef organization with the configured organization name
   - Associates the user with the organization
   - Generates and saves authentication key files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

4. **Alternative Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Similar to the main script but only deploys Chef Infra Server without Automate
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

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial Chef administrator user

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`: Chef Server configuration directory
- `/etc/chef/`: Chef client configuration directory
- Generated PEM files: `<username>.pem` and `<orgname>-validator.pem` in the current directory

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

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

# Verify user creation
sudo chef-server-ctl user-list | grep <username>

# Verify organization creation
sudo chef-server-ctl org-list | grep <orgname>

# Check generated key files
ls -la <username>.pem
ls -la <orgname>-validator.pem

# Verify Chef Automate UI access
curl -k https://localhost/api/v0/auth/version

# Check services
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Log files
sudo tail -f /var/log/chef-server/nginx/access.log
sudo tail -f /var/log/chef-server/nginx/error.log
sudo tail -f /var/log/chef-automate/automate-deployment.log

# API check
curl -s -k https://localhost/api/v0/auth/version | jq
```