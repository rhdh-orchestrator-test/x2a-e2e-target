---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
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
     - Username (e.g., 'jtonello')
     - Full name (e.g., 'John Tonello')
     - Email (e.g., 'jtonello@chef.lab')
     - Password (e.g., 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name (e.g., 'lab')
     - Full name (e.g., 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
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
- **Usage context**: Used to create the initial Chef user account

### Chef User Authentication Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef user, saved to a .pem file

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file
- **Usage context**: Validator key for the Chef organization, saved to a .pem file

### Chef User Identity

- **Variable(s)**: `username`, `longusername`, `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the Chef user identity

### Chef Organization Identity

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the Chef organization

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname change)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- Generated user key file (e.g., jtonello.pem)
- Generated organization validator key file (e.g., lab-validator.pem)
- Chef Automate configuration files (in default installation path)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should exist and be executable
./chef-automate version  # Should return version information

# Chef Automate and Chef Infra Server status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/health  # Should return healthy status

# Chef user and organization
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Authentication keys
ls -la ./${username}.pem  # Should exist and have proper permissions
ls -la ./${orgname}-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep 443  # Alternative check for listening ports

# Web UI access
curl -k -I https://localhost  # Should return HTTP 200 OK
curl -k -I https://localhost/organizations/${orgname}  # Should return HTTP 200 OK

# Logs
sudo journalctl -u chef-automate  # Check for any errors
sudo chef-automate logs  # View Chef Automate logs

# Resources
free -m  # Check available memory
df -h  # Check disk space
top -n 1  # Check CPU usage
```