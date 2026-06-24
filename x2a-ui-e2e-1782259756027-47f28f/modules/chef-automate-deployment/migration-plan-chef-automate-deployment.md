---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts configure system settings, download the Chef Automate CLI, deploy the services, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Configuration management server
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

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Resources: curl command, file permissions change

3. **Service Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate CLI command

4. **Service Deployment (Infra Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate CLI command

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user in Chef Infra Server with the configured details
   - Saves the user's private key to a .pem file
   - Command: `chef-server-ctl user-create $username $longusername $useremail "${userpassword}" --filename $userfilename`
   - Resources: chef-server-ctl command

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an organization in Chef Infra Server
   - Associates the previously created user with the organization
   - Saves the organization validator key to a .pem file
   - Command: `chef-server-ctl org-create $orgname "${longorgname}" --association_user $username --filename $orgfilename`
   - Resources: chef-server-ctl command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (Chef Automate handles its dependencies)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 5 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Infra Server User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user in Chef Infra Server

### Chef Infra Server User Details

- **Variable(s)**: `username`, `longusername`, `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user in Chef Infra Server

### Chef Infra Server Organization Details

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial organization in Chef Infra Server

### Chef User Private Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the created user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the created organization

## Checks for the Migration

**Files to verify**:
- /etc/chef/automate-credentials.toml (generated by Chef Automate)
- ${username}.pem (user private key)
- ${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None (deployment scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list | grep $(hostname)

# Verify organization creation
sudo chef-server-ctl org-list | grep $(orgname)

# Verify key files
ls -la ${username}.pem
ls -la ${orgname}-validator.pem

# Check services
systemctl status chef-automate
sudo chef-automate service-versions

# Check web UI accessibility
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# Check Chef Infra Server API
curl -k https://localhost/organizations/${orgname}/_ping

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Logs
sudo chef-automate logs
journalctl -u chef-automate
```