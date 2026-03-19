# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations. There are two scripts: one for deploying both Chef Automate and Chef Infra Server, and another for deploying only Chef Infra Server.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the first script, standalone in the second script

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
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the CLI executable
   - Resources: curl command, file permissions change (2)

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

4. **Product Deployment (Infra Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user in Chef Infra Server with:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
   - Saves user key to jtonello.pem (derived from username)
   - Resources: chef-server-ctl user-create command (1)

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an organization in Chef Infra Server with:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
   - Associates the previously created user with the organization
   - Saves organization validator key to lab-validator.pem (derived from org name)
   - Resources: chef-server-ctl org-create command (1)

## Dependencies

**External cookbook dependencies**: None (these are standalone bash scripts)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Infra Server configuration directory)
- User key file: jtonello.pem (or as configured)
- Organization validator key: lab-validator.pem (or as configured)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for both Chef Automate and Chef Infra Server)
- Network interfaces: All interfaces by default

**Templates rendered**:
- No templates are explicitly rendered in these scripts

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate API check
curl -k https://localhost/api/v0/auth/version

# Chef Infra Server API check
curl -k https://localhost/organizations

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la jtonello.pem
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem
sudo chef-server-ctl org-show lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-automate logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# Web UI access
curl -k -I https://localhost
curl -k -I https://localhost/organizations/lab

# System resources
df -h
free -m
top -n 1
```