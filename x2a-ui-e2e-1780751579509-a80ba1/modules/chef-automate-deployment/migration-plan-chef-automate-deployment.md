---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a Bash script-based deployment of Chef Automate and Chef Infra Server, not a traditional Chef cookbook. The scripts configure hostname, system parameters, download and deploy Chef Automate CLI, and set up initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Central management platform for Chef
  - Location/Path: Deployed via chef-automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed via chef-automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment consists of Bash scripts rather than Chef cookbooks. The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate with Infra Server using the CLI
   - Creates initial user with specified credentials
   - Creates initial organization and associates the user
   - Resources: hostname configuration, sysctl parameters, Chef Automate CLI, user creation, organization creation

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets system hostname to the configured value
   - Configures the same kernel parameters
   - Downloads Chef Automate CLI
   - Deploys only the Infra Server product
   - Creates initial user with specified credentials
   - Creates initial organization and associates the user
   - Resources: hostname configuration, sysctl parameters, Chef Automate CLI, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None (uses Bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef user

### User Authentication Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated during deployment and saved to file
- **Usage context**: Authentication key for the created user

### Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated during deployment and saved to file
- **Usage context**: Validator key for the created organization

### User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Email address for the created Chef user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- /proc/sys/vm/max_map_count (modified by sysctl)
- /proc/sys/vm/dirty_expire_centisecs (modified by sysctl)
- chef-automate executable (downloaded to current directory)
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (Bash scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the created user
ls -la /path/to/user.pem  # Verify user key exists and has proper permissions

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization
ls -la /path/to/org-validator.pem  # Verify org validator key exists

# Web UI access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/_status  # Should return status information

# Network listening
netstat -tulpn | grep :443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep :443  # Alternative to netstat

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate logs  # Alternative way to view logs

# API access (using the generated key)
knife user list -s https://localhost/organizations/orgname -k /path/to/user.pem -u username  # Should list users without errors
```