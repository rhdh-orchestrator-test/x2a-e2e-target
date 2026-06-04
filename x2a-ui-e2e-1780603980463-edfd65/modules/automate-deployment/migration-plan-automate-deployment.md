---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup, system tuning, and server deployment.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Single instance deployment
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate or standalone

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate AND Chef Infra Server with a single command
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: sysctl (2), curl/gunzip, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys ONLY Chef Infra Server (without Automate)
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Resources: sysctl (2), curl/gunzip, chef-automate deploy, chef-server-ctl (2)

The key difference between the scripts is that `deploy-automate.sh` installs both Chef Automate and Chef Infra Server, while `deploy-chef-server.sh` installs only Chef Infra Server.

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

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/chef-server.rb` (Chef Server configuration)
- `/etc/chef/client.rb` (Chef Client configuration)
- User PEM file: `<username>.pem` (in current directory)
- Organization validator PEM file: `<orgname>-validator.pem` (in current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server)
- Network interfaces: All interfaces (0.0.0.0)

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

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep <username>
sudo chef-server-ctl org-list | grep <orgname>

# PEM file verification
ls -la <username>.pem
ls -la <orgname>-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service health checks
curl -k https://localhost/api/_status
curl -k https://localhost/organizations/<orgname>

# Log verification
sudo journalctl -u chef-automate
sudo journalctl -u chef-server

# Chef server API access test (using the generated PEM file)
knife user list -s https://localhost/organizations/<orgname> -u <username> -k <username>.pem

# Chef Automate UI access
curl -k https://localhost/api/v0/auth/version
```