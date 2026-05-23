---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-setup

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise automation platform
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Resources: curl, chmod commands

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flags

4. **Chef Infra Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server (without Automate)
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Setup** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates initial user with specified credentials
   - Creates organization and associates user with it
   - Generates and saves user and organization PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create commands

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

### Chef User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the admin user

### Chef Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the organization validator

### Chef User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Email address for the admin user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ~/chef-automate (the downloaded CLI executable)
- ~/{username}.pem (user PEM file)
- ~/{orgname}-validator.pem (organization validator PEM file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ~/chef-automate  # Should exist and be executable
~/chef-automate version  # Should display version information

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured orgname

# PEM files
ls -la ~/${username}.pem  # Should exist
ls -la ~/${orgname}-validator.pem  # Should exist

# Web UI access
curl -k https://localhost  # Should return Chef Automate login page HTML
curl -k https://localhost/_status  # Should return status information

# Network listening
sudo netstat -tulpn | grep ':443'  # Should show services listening on port 443
sudo ss -tlnp | grep ':443'  # Alternative way to check listening ports

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate logs  # Alternative way to check Chef Automate logs
```