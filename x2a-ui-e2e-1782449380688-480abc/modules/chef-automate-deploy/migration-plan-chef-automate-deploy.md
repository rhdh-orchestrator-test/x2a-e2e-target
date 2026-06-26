---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters for Elasticsearch:
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
     - Username, full name, email, password
     - Generates user PEM file
   - Creates a Chef organization with:
     - Organization short name and full name
     - Associates the created user with the organization
     - Generates organization validator PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 4 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef user

### Chef Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef organization

### Chef Automate Credentials

- **Variable(s)**: Not explicitly defined in script
- **Source file(s)**: Generated during installation
- **Current storage**: Generated during Chef Automate deployment
- **Usage context**: Web UI access to Chef Automate

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname change)
- /proc/sys/vm/max_map_count (for sysctl parameter)
- /proc/sys/vm/dirty_expire_centisecs (for sysctl parameter)
- ./chef-automate (downloaded binary)
- ./${username}.pem (user key file)
- ./${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate binary
ls -la ./chef-automate
file ./chef-automate  # Should be executable

# Chef Automate service status
sudo chef-automate status

# Chef Infra Server status
sudo chef-automate status infra-server

# User and organization verification
ls -la ./${username}.pem  # Should exist and be readable
ls -la ./${orgname}-validator.pem  # Should exist and be readable

# Web UI access
curl -k https://localhost/api/v0/auth/version  # Should return version info
curl -k https://localhost/api/_status  # Should return status info

# Chef Server API access
knife user list -s https://localhost/organizations/${orgname} -k ./${username}.pem -u ${username}  # Should list the created user
knife org list -s https://localhost -k ./${username}.pem -u ${username}  # Should list the created organization

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Logs
sudo chef-automate logs
journalctl -u chef-automate
```