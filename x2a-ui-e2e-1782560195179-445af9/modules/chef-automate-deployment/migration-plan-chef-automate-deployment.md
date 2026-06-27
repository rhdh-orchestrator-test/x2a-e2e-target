---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA automatically

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (typically 443)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with automatic MLSA acceptance
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 5 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Chef Admin User Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the admin user to access Chef Infra Server

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Validator key used for bootstrapping nodes to the Chef organization

### Chef Admin User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Email address for the Chef admin user

### Chef Admin Username

- **Variable(s)**: `username`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Username for the Chef admin user

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `~/${username}.pem` - User key file
- `~/${orgname}-validator.pem` - Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list  # Should include the configured username
ls -la ~/${username}.pem  # Verify user key exists and has proper permissions

# Verify organization creation
sudo chef-server-ctl org-list  # Should include the configured organization name
ls -la ~/${orgname}-validator.pem  # Verify organization validator key exists

# Verify Chef Automate UI
curl -k https://localhost  # Should return Chef Automate UI HTML
curl -k https://localhost/_status  # Should return status information

# Verify Chef Infra Server API
curl -k https://localhost/organizations/${orgname}  # Should return organization info

# Check logs
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Verify login works
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ~/${username}.pem
```