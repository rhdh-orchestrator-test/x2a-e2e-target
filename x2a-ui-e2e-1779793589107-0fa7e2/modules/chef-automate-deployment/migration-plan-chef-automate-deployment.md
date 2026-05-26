---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial user with specified credentials:
     - Username, full name, email, and password
     - Saves user key to a PEM file
   - Creates organization with specified details:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

The second script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Chef User Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated during deployment and saved to local file
- **Usage context**: Authentication key for the admin user to access Chef Infra Server API

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated during deployment and saved to local file
- **Usage context**: Authentication key for bootstrapping new nodes to the Chef organization

### Chef Automate License Agreement

- **Variable(s)**: `--accept-terms-and-mlsa=true`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Acceptance of Chef's Master License and Services Agreement

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname change)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- chef-automate executable in current directory
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) or specific IP if configured

**Templates rendered**:
None (script-based deployment)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la chef-automate  # Should exist and be executable
./chef-automate version  # Should show version information

# Chef Automate and Chef Infra Server status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/health  # Should return health status

# Chef Infra Server functionality
sudo chef-server-ctl status  # Should show all services running
ls -la jtonello.pem  # Should exist (replace with actual username)
ls -la lab-validator.pem  # Should exist (replace with actual org name)

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Network listening
sudo netstat -tulpn | grep ':443'  # Should show Chef Automate/Infra Server listening
sudo ss -tlnp | grep ':443'  # Alternative check for listening ports

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate logs  # Alternative way to view Chef Automate logs

# API functionality test (requires knife configured with admin user)
knife user list  # Should list users including the admin user
knife org list  # Should list organizations including the created org
knife ssl check  # Should verify SSL certificate
```