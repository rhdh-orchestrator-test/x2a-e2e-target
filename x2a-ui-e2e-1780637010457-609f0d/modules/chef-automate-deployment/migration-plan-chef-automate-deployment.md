---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring system parameters, installing Chef Automate CLI, deploying Chef products, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate, user and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads the Chef Automate CLI package from Chef's package repository
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server products
   - Accepts terms and MLSA (Master License and Services Agreement)
   - Resources: chef-automate deploy command with product flags

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username, full name, email, and password
     - Generates and saves user key file (e.g., 'jtonello.pem')
   - Creates a Chef organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Generates and saves organization validator key file (e.g., 'lab-validator.pem')
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

The script `setup-automate/deploy-chef-server.sh` performs similar operations but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (this is a standalone deployment script)
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User Key File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the Chef user, used for API authentication

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the Chef organization, used for node bootstrapping

### Chef User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used for the Chef user account creation

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)
- Chef Automate configuration files (typically in /etc/chef-automate/)
- Chef Server configuration files (typically in /etc/opscode/)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Server API)
- Network interfaces: All interfaces (0.0.0.0) or specific IP if configured

**Templates rendered**:
None (this is a deployment script, not a Chef cookbook with templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should exist and be executable
./chef-automate version  # Should return version information

# Chef Automate status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/status  # Should return status JSON

# Chef Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Key files
ls -la $userfilename  # Should exist and contain RSA private key
ls -la $orgfilename  # Should exist and contain RSA private key

# Web UI access
curl -k https://localhost  # Should redirect to Chef Automate login page

# Network listening
netstat -tulpn | grep :443  # Should show services listening on port 443
ss -tlnp | grep :443  # Alternative to netstat

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate logs  # Alternative way to view Chef Automate logs

# Chef Server API test (using the generated user key)
knife user list -s https://localhost/organizations/$orgname -u $username -k $userfilename  # Should list users without errors
```