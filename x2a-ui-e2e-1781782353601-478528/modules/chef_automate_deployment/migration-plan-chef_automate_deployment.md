---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef_automate_deployment

**TLDR**: This module consists of two Bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Resources: curl, chmod (2)

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server with the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

   **OR**

   **Chef Infra Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server with the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Creates initial user with:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem (derived from username)
   - Creates initial organization with:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates with created user
     - Saves validator key to lab-validator.pem (derived from org name)
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, hostnamectl
**Service dependencies**: None

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
- **Usage context**: This password is used for the initial Chef admin user created during setup

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef-automate/
- User key file: jtonello.pem (or configured username)
- Organization validator key: lab-validator.pem (or configured org name)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment scripts don't use templates)

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

# Chef Automate UI access
curl -k https://localhost/api/v0/auth/version

# Chef Server API access
curl -k https://localhost/organizations

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test user authentication
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/chef-server
```