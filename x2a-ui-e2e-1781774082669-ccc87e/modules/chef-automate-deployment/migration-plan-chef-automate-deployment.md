---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server products, and creates initial user and organization configurations. The script is designed to run on a Linux system and sets up a complete Chef server environment.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, chmod (2)

3. **Chef Automate and Chef Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

4. **User Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the following attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Generates user key file: jtonello.pem
   - Resources: chef-server-ctl user-create (1)

5. **Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef organization with the following attributes:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the previously created user
     - Generates organization validator key: lab-validator.pem
   - Resources: chef-server-ctl org-create (1)

Note: The `setup-automate/deploy-chef-server.sh` script follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account for authentication to Chef Infra Server and Chef Automate

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- chef-automate executable in the directory where the script was run
- User PEM file (jtonello.pem by default)
- Organization validator PEM file (lab-validator.pem by default)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname (automate.chef.lab by default)
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la chef-automate  # Should exist and be executable
./chef-automate version  # Should return version information

# Chef Automate and Chef Infra Server
curl -k https://localhost/api/v0/status  # Should return status information for Chef Automate
curl -k https://localhost/organizations  # Should return organizations for Chef Infra Server

# User and organization
ls -la jtonello.pem  # Should exist (or the configured username.pem)
ls -la lab-validator.pem  # Should exist (or the configured orgname-validator.pem)

# Chef Server API access
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should list the created user
knife org list -s https://localhost -u jtonello -k jtonello.pem  # Should list the created organization

# Service status
sudo chef-automate status  # Should show all services running
sudo chef-server-ctl status  # Should show all Chef Server services running

# Network listening
sudo netstat -tulpn | grep ':443'  # Should show services listening on port 443
sudo ss -tlnp | grep ':443'  # Alternative to netstat

# Logs
sudo chef-automate logs  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Server logs

# UI access
echo "Try accessing https://$(hostname) in a web browser and login with username: jtonello, password: password (or as configured)"
```