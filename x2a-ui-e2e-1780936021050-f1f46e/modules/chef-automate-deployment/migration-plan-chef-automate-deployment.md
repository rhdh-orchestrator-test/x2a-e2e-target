---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate with Infra Server, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Deployed with default configuration

- **Chef Infra Server**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, chmod (2)

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial user with specified credentials:
     - Username, full name, email, and password
     - Saves user key to a .pem file
   - Creates organization with specified details:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 5 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Automate Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Chef User Authentication Keys

- **Variable(s)**: `userfilename` (user key), `orgfilename` (organization validator key)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated during deployment and saved to local files
- **Usage context**: Authentication keys for Chef Infra Server API access

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Infra Server configuration directory)
- ${username}.pem (User authentication key)
- ${orgname}-validator.pem (Organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None (deployment uses default templates from the Chef Automate package)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Automate services
sudo chef-automate service-versions

# Chef Automate API check
curl -k https://localhost/api/v0/auth/version

# Chef Infra Server status
sudo chef-server-ctl status

# Chef Infra Server organization check
sudo chef-server-ctl org-list | grep ${orgname}

# Chef Infra Server user check
sudo chef-server-ctl user-list | grep ${username}

# Verify user authentication
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ${username}.pem

# Check generated credential files
ls -la ${username}.pem
ls -la ${orgname}-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service logs
sudo journalctl -u chef-automate
sudo chef-automate logs

# Verify web UI access
curl -k -I https://localhost

# Memory usage
free -m
ps aux | grep chef | sort -k 4 -r | head -10
```