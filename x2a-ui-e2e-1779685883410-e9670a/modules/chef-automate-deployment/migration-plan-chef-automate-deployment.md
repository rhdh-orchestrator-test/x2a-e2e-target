---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup, system tuning, and server deployment.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Includes Chef Infra Server product

- **Chef Infra Server**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Tunes kernel parameters for Chef Automate:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Generates user key file (default: 'jtonello.pem')
   - Creates a Chef organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Generates organization validator key (default: 'lab-validator.pem')
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, hostnamectl, sysctl
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 3 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword` (default: 'password')
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef admin user

### Chef User Key File

- **Variable(s)**: `userfilename` (default: 'jtonello.pem')
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: generated file
- **Usage context**: Authentication key for the Chef admin user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (default: 'lab-validator.pem')
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: generated file
- **Usage context**: Authentication key for the Chef organization validator

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- User key file (default: jtonello.pem)
- Organization validator key file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment uses CLI tools rather than templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname (default: automate.chef.lab)
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/status  # Should return status information

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username (default: jtonello)
sudo chef-server-ctl org-list  # Should include the configured organization (default: lab)

# Key file verification
ls -la $(pwd)/${username}.pem  # Should exist and have proper permissions
ls -la $(pwd)/${orgname}-validator.pem  # Should exist and have proper permissions

# Test API access with the generated key
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ${username}.pem  # Should return user list

# Network listening
netstat -tulpn | grep :443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep :443  # Alternative check for listening ports

# Service status
systemctl status chef-automate  # Should be active
```