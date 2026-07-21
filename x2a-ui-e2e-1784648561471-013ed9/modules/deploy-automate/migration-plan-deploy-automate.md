---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: deploy-automate

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using a bash script. It configures system settings, downloads and installs Chef Automate CLI, deploys the products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: Default ports (typically 443)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flags

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates an initial user with the following attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates an organization with the following attributes:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires standard Linux system services

## Credentials

**Detection Summary**: 1 credential detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user key file, default: jtonello.pem)
- ${orgname}-validator.pem (organization validator key, default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly rendered by the script. Chef Automate handles its own configuration.

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname (automate.chef.lab)
sysctl vm.max_map_count  # Should return 262144
sysctl vm.dirty_expire_centisecs  # Should return 20000

# Chef Automate CLI
ls -la chef-automate  # Should show the executable file
./chef-automate version  # Should show version information

# Service status
sudo systemctl status chef-automate  # Should show active (running)

# Web UI accessibility
curl -k https://localhost/api/v0/health  # Should return health status
curl -k https://localhost  # Should return HTTP 200 or redirect to login page

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user (jtonello)
sudo chef-server-ctl org-list  # Should include the created organization (lab)

# Key files
ls -la jtonello.pem  # Should exist and have proper permissions
ls -la lab-validator.pem  # Should exist and have proper permissions

# Network listening
sudo netstat -tulpn | grep LISTEN  # Should show services listening on expected ports
sudo ss -tulpn | grep LISTEN  # Alternative to netstat

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs

# API accessibility (requires user key)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should list users without errors
```