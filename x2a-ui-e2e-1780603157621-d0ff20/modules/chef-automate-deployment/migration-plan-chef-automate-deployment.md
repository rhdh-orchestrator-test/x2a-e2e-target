---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
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
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username: configured value (default: 'jtonello')
     - Full name: configured value (default: 'John Tonello')
     - Email: configured value (default: 'jtonello@chef.lab')
     - Password: configured value (default: 'password')
     - Saves user key to a PEM file
   - Creates a Chef organization with:
     - Short name: configured value (default: 'lab')
     - Full name: configured value (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (this is a standalone script)
**System package dependencies**: curl, gunzip, sudo
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
- **Usage context**: Password for the Chef Infra Server admin user

### Chef User Authentication Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the Chef Infra Server admin user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Validator key for the Chef organization

### Chef Automate Admin Credentials

- **Variable(s)**: Not explicitly defined in script, but created during deployment
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated during Chef Automate deployment
- **Usage context**: Admin credentials for Chef Automate web UI

### Chef Server API Endpoint

- **Variable(s)**: Implicitly defined by `hostname`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: API endpoint for Chef Server interactions

## Checks for the Migration

**Files to verify**:
- /etc/chef/client.rb (if created)
- /etc/chef/client.pem (if created)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)
- /etc/hosts (for hostname entry)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Server API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**: None (this script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/auth/version  # Check Chef Automate API
curl -k https://localhost/api/_status  # Check Chef Infra Server API

# Chef Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Authentication verification
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ${username}.pem  # Should list users
knife client list -s https://localhost/organizations/${orgname} -u ${username} -k ${username}.pem  # Should list clients

# Network listening
sudo netstat -tulpn | grep ':443'  # Should show Chef Automate and Chef Server listening
sudo ss -tlnp | grep ':443'  # Alternative check for listening ports

# Process verification
ps aux | grep chef
ps aux | grep automate

# Log verification
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Web UI access
curl -k -I https://localhost  # Should return HTTP 200 OK
```