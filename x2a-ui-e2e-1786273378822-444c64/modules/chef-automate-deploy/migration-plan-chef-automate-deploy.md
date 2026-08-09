---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's central server for managing infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username: Configured value (default: 'jtonello')
     - Full name: Configured value (default: 'John Tonello')
     - Email: Configured value (default: 'jtonello@chef.lab')
     - Password: Configured value (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization:
     - Short name: Configured value (default: 'lab')
     - Full name: Configured value (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None (this is a standalone script)
**System package dependencies**: curl, sudo, hostnamectl, sysctl
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 5 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User Information

- **Variable(s)**: `username`, `longusername`, `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef Organization Information

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef organization

### User Key File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated during execution
- **Usage context**: Stores the private key for the created Chef user

### Organization Validator Key File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated during execution
- **Usage context**: Stores the validator key for the created Chef organization

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `jtonello.pem` (or configured username.pem) in the current directory
- `lab-validator.pem` (or configured orgname-validator.pem) in the current directory
- Chef Automate configuration files (typically in `/etc/chef-automate/`)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (this script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/status  # Should return status information

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# Key files
ls -la jtonello.pem  # Or configured username.pem - should exist and have proper permissions
ls -la lab-validator.pem  # Or configured orgname-validator.pem - should exist and have proper permissions

# Connectivity test
knife ssl check -s https://localhost/organizations/lab  # Should succeed without SSL errors

# Service listening
netstat -tulpn | grep :443  # Should show services listening on port 443
ss -tlnp | grep :443  # Alternative to netstat

# Logs
sudo journalctl -u chef-automate  # Check for any errors
sudo chef-automate logs  # View Chef Automate logs

# Web UI access
curl -k https://localhost/  # Should return the Chef Automate login page
```