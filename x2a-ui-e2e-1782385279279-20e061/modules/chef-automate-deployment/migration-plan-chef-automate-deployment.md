---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up a Chef server environment with a single user and organization, configuring system parameters and downloading the necessary Chef components.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chef-automate CLI, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chef-automate CLI, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but requires systemd for hostname configuration

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the Chef user

### Chef Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the Chef organization

### Chef User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for Chef user creation and notifications

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- /proc/sys/vm/max_map_count (modified by sysctl)
- /proc/sys/vm/dirty_expire_centisecs (modified by sysctl)
- chef-automate executable in current directory
- User PEM file (e.g., jtonello.pem) in current directory
- Organization validator PEM file (e.g., lab-validator.pem) in current directory

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# PEM files
ls -la *.pem  # Should show user and organization validator PEM files
file jtonello.pem  # Should be a valid PEM file
file lab-validator.pem  # Should be a valid PEM file

# Network connectivity
ss -tlnp | grep :443  # Should show Chef Automate/Server listening
curl -k https://localhost  # Should return Chef Automate UI

# Chef API verification
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem --no-editor  # Should list users
knife client list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem --no-editor  # Should list clients

# Log verification
sudo journalctl -u chef-automate  # Check for any errors
sudo chef-automate logs  # Check component logs

# Disk space
df -h  # Verify sufficient disk space for Chef Automate/Server
```