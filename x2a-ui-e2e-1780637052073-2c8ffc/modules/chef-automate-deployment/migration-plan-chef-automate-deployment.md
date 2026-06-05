---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It configures a single instance with user and organization setup. The script sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates initial user and organization entities.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**:
  - Location/Path: Deployed on the local system
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

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA
   - Resources: curl, gunzip, chmod, chef-automate deploy

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
     - Associates the created user
     - Generates organization validator key (default: 'lab-validator.pem')
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected in the deployment script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- User key file: `<username>.pem` (default: jtonello.pem)
- Organization validator key: `<orgname>-validator.pem` (default: lab-validator.pem)
- Chef Automate configuration: `/etc/chef-automate/config.toml`

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment script doesn't use templates)

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

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la jtonello.pem
chmod 400 jtonello.pem  # Ensure proper permissions

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem
chmod 400 lab-validator.pem  # Ensure proper permissions

# Test API access with the created user
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Web UI access
curl -k https://localhost/api/v0/auth/status  # Chef Automate API check
curl -k https://localhost/organizations/lab    # Chef Infra Server API check

# Service status
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Resource usage
df -h /var    # Check disk space
free -m       # Check memory usage
top -n 1 -b   # Check CPU usage
```