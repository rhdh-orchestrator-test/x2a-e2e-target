---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts handle system prerequisites, download Chef Automate CLI, deploy the products, and set up initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Includes Chef Infra Server product

- **Chef Infra Server**:
  - Location/Path: Deployed on the local system
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
   - Configures kernel parameters for Chef Automate:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

4. **Alternative Deployment - Chef Infra Server Only** (`setup-automate/deploy-chef-server.sh`):
   - Similar to the main script but only deploys Chef Infra Server without Automate
   - Uses the same system configuration and user/organization setup steps
   - Only difference is the `--product` flag in the deployment command
   - Resources: Same as above but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account for authentication to Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- User PEM file (default: jtonello.pem)
- Organization validator PEM file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (bash scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /etc/hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should return 262144
sysctl vm.dirty_expire_centisecs  # Should return 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should show the executable file
./chef-automate version  # Should show version information

# Service status
sudo systemctl status chef-automate  # Should be active (running)

# Network listening
ss -tlnp | grep ':443'  # Should show Chef Automate listening on port 443
curl -k https://localhost/api/v0/status  # Should return status information

# User and organization verification
ls -la jtonello.pem  # Should show the user key file
ls -la lab-validator.pem  # Should show the organization validator key file

# API access test
curl -s -k https://localhost/api/v0/auth/token -d '{"username":"jtonello", "password":"password"}' -H "Content-Type: application/json"  # Should return a token

# Chef Infra Server verification
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should show the created user
knife org list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should show the created organization

# Logs
sudo journalctl -u chef-automate -n 50  # Check recent logs
sudo chef-automate status  # Should show all services running

# Configuration backup verification
sudo chef-automate backup status  # Check if backups are configured
```