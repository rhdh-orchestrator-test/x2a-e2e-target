---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization settings

- **Chef Infra Server**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization settings

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets the hostname using `hostnamectl set-hostname`
   - Configures kernel parameters with `sysctl`:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod
   - Resources: curl command, chmod command (2)

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

4. **Chef Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

5. **User and Organization Setup** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user with chef-server-ctl user-create
   - Creates an organization with chef-server-ctl org-create
   - Associates the user with the organization
   - Generates and saves PEM files for authentication
   - Resources: chef-server-ctl commands (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but requires systemd for hostnamectl

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef user

### Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef organization

### User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Email address for the Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user authentication key)
- ${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

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
curl -k https://localhost/api/v0/health  # Should return health status

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Authentication key verification
ls -la ${username}.pem  # Should exist
ls -la ${orgname}-validator.pem  # Should exist

# Test authentication with the generated keys
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ${username}.pem  # Should succeed

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate and Chef Infra Server listening
ss -tlnp | grep 443  # Alternative check for listening ports

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-automate logs  # Alternative way to check logs
```