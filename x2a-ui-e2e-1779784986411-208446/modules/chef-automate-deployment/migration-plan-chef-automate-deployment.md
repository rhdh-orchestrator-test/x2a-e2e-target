---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a single instance of these services on a VM, configures system parameters, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user with the following attributes:
     - Username: Configured value (default: 'jtonello')
     - Full name: Configured value (default: 'John Tonello')
     - Email: Configured value (default: 'jtonello@chef.lab')
     - Password: Configured value (default: 'password')
     - Saves user key to a .pem file
   - Creates an organization with the following attributes:
     - Short name: Configured value (default: 'lab')
     - Full name: Configured value (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for hostname configuration

## Credentials

**Detection Summary**: 3 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef Infra Server user

### User PEM Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated and stored as a file
- **Usage context**: Authentication key for the created user to access Chef Infra Server

### Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated and stored as a file
- **Usage context**: Authentication key for validating new nodes joining the Chef organization

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `~/${username}.pem` (user key file)
- `~/${orgname}-validator.pem` (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/status  # Should return 200 OK with status JSON

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl user-show jtonello  # Replace with actual username

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization
sudo chef-server-ctl org-show lab  # Replace with actual organization name

# Key file verification
ls -la ~/*.pem  # Should show user and organization validator keys
file ~/*.pem  # Verify they are valid PEM files

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443
sudo lsof -i :443

# Service logs
sudo journalctl -u chef-automate -n 100
sudo chef-automate system-logs
```