# Migration Plan: Chef Automate Setup

**TLDR**: This module consists of Bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port: 443
  - Key Config: Deployed with `--product automate` flag
  
- **Chef Infra Server**:
  - Location/Path: Installed via Chef Automate CLI
  - Port: 443
  - Key Config: Deployed with `--product infra-server` flag
  - User: Configured with chef-server-ctl
  - Organization: Configured with chef-server-ctl

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of Bash scripts that perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl to the value specified in variables
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with specified products
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **Chef Server User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user with chef-server-ctl user-create command
   - Creates an organization with chef-server-ctl org-create command
   - Associates the user with the organization
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

The `setup-automate/deploy-chef-server.sh` script follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None

**System package dependencies**: 
- curl
- gunzip
- sudo

**Service dependencies**: 
- Chef Automate CLI
- Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef/jtonello.pem
- /etc/chef/lab-validator.pem
- Chef Automate configuration files (generated during deployment)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (Bash scripts don't use templates)

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
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la /etc/chef/jtonello.pem
ls -la /etc/chef/lab-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# Chef Server API access
knife user list -s https://localhost/organizations/lab -k /etc/chef/jtonello.pem -u jtonello

# Logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Service health
sudo chef-automate service-versions
sudo chef-automate status
```