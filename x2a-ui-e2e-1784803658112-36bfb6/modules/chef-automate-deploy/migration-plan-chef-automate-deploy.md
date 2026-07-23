---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
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

The module consists of bash scripts rather than Chef recipes. These scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the CLI executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Saves the user's private key to a .pem file
   - Creates a Chef organization with the configured name
   - Associates the user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

4. **Chef Server Only Installation** (`setup-automate/deploy-chef-server.sh`):
   - Similar to the deploy-automate.sh script but only installs the Chef Infra Server product
   - Performs the same system configuration, user creation, and organization setup
   - Resources: hostnamectl, sysctl (2), curl, gunzip, chmod, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly managed in the scripts

## Credentials

**Detection Summary**: 5 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User Private Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated and saved to local file
- **Usage context**: Authentication key for the Chef user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated and saved to local file
- **Usage context**: Authentication key for the Chef organization

### Chef User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for the Chef user account creation

### Chef User Details

- **Variable(s)**: `username`, `longusername`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for the Chef user account creation

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (bash scripts, not Chef templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la ~/jtonello.pem
chmod 400 ~/jtonello.pem

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la ~/lab-validator.pem
chmod 400 ~/lab-validator.pem

# API connectivity test
curl -k https://localhost/organizations/lab

# Web UI accessibility
curl -k -I https://localhost/

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep ':443'

# Service logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Authentication test
knife user list -s https://localhost/organizations/lab -u jtonello -k ~/jtonello.pem

# System resources
df -h
free -m
top -bn1 | head -20
```