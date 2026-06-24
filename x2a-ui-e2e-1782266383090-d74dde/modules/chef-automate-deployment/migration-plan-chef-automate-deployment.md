---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate with Infra Server, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Deployed with Chef Infra Server

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the value specified in the hostname variable
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified username, name, email, and password
   - Creates a Chef organization with specified organization name
   - Associates the user with the organization
   - Generates and saves user and organization PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

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
- **Current storage**: Generated PEM file
- **Usage context**: Authentication key for the Chef user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated PEM file
- **Usage context**: Validator key for the Chef organization

### Chef User Information

- **Variable(s)**: `username`, `longusername`, `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef Organization Information

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the Chef organization

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
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
curl -k https://localhost/api/_status  # Should return status information

# Chef Infra Server status
sudo chef-server-ctl status
curl -k https://localhost/organizations/${orgname}  # Should return organization info

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Key files
ls -la ~/${username}.pem  # Should exist and have proper permissions
ls -la ~/${orgname}-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 100
sudo chef-automate logs

# Chef server logs
sudo chef-server-ctl tail

# Test API access with the generated keys
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ~/${username}.pem --no-ssl-verify
```