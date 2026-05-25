---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up a complete Chef infrastructure environment with a single user and organization, configuring system parameters and installing the necessary components.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `chef-automate deploy` command
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with `chef-automate deploy` command
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: hostnamectl, sysctl (2), curl, chef-automate, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
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
- **Current storage**: hardcoded
- **Usage context**: This credential is used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `~/${username}.pem` - User key file (e.g., jtonello.pem)
- `~/${orgname}-validator.pem` - Organization validator key file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname (e.g., automate.chef.lab)
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured user (e.g., jtonello)
sudo chef-server-ctl org-list  # Should include the configured organization (e.g., lab)

# Key files
ls -la ~/${username}.pem  # Should exist (e.g., ~/jtonello.pem)
ls -la ~/${orgname}-validator.pem  # Should exist (e.g., ~/lab-validator.pem)

# Network listening
netstat -tulpn | grep 443  # Should show services listening on port 443
ss -tlnp | grep 443  # Alternative to netstat

# Web UI access
curl -k https://localhost  # Should return Chef Automate UI content
curl -k https://localhost/_status  # Should return status information

# API access (using the generated key)
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ~/${username}.pem  # Should list users

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-automate logs  # Alternative way to check logs

# Service health
sudo chef-automate service-versions  # Should show all service versions
sudo chef-automate status  # Should show all services in a running state
```