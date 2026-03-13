# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two Bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up a complete Chef infrastructure environment with user and organization creation. No actual Chef cookbook is present - these are standalone Bash scripts that download and configure Chef products.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with hostname, user credentials, and organization details

- **Chef Infra Server**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with the same hostname, user credentials, and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations through Bash scripts rather than Chef recipes:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for Chef Automate:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with a single command
   - Creates a user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates an organization:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Saves organization validator key to lab-validator.pem

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures the same kernel parameters
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server (not Automate)
   - Creates the same user and organization with identical configuration

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- jtonello.pem (user key file)
- lab-validator.pem (organization validator key file)
- Chef Automate configuration files (installed by the deployment process)
- Chef Infra Server configuration files (installed by the deployment process)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Unix sockets: None explicitly defined
- Network interfaces: All interfaces (default)

**Templates rendered**: None (not a Chef cookbook)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# Kernel parameter verification
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
sudo chef-server-ctl org-show lab

# Key file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://automate.chef.lab

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Log verification
sudo journalctl -u chef-automate
sudo journalctl -u chef-server

# Authentication test
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem
```