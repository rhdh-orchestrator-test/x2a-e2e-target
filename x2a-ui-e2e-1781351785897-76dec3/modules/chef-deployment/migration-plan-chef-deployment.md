---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Server

**Configured Instances**:
- **Chef Automate Server**: A complete Chef Automate server with integrated Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A standalone Chef Infra Server (without Automate)
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate with Chef Infra Server using the CLI
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname, sysctl (2), curl, file permissions, chef-automate CLI, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) using the CLI
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname, sysctl (2), curl, file permissions, chef-automate CLI, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user authentication key)
- ~/${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (shell scripts with variables)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (if deployed with Automate)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username
ls -la ~/$userfilename

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
ls -la ~/$orgfilename

# Web UI access
curl -k https://localhost/_status
curl -k https://localhost/organizations/$orgname

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service status
systemctl status chef-automate
systemctl status chef-server

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50
```