---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with user and organization configuration. The script configures system parameters, downloads the Chef Automate CLI, deploys Chef products, and creates initial user and organization entities.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Main automation platform for Chef
  - Location/Path: Deployed to the local system
  - Port/Socket: 443 (HTTPS)
  - Key Config: Accepts terms and MLSA agreement
  
- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed alongside Chef Automate
  - Port/Socket: 443 (HTTPS)
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
   - Resources: curl, gunzip, chmod

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server products
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command

4. **User Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the following attributes:
     - Username: Configured value (default: 'jtonello')
     - Full name: Configured value (default: 'John Tonello')
     - Email: Configured value (default: 'jtonello@chef.lab')
     - Password: Configured value (default: 'password')
   - Saves user key to a PEM file
   - Resources: chef-server-ctl user-create

5. **Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef organization with the following attributes:
     - Short name: Configured value (default: 'lab')
     - Full name: Configured value (default: 'Chef Lab')
   - Associates the previously created user with the organization
   - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same process but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires proper system resources for Chef Automate and Chef Infra Server

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- Chef Automate configuration files (generated during deployment)
- User PEM file: `<username>.pem` (default: jtonello.pem)
- Organization validator PEM file: `<orgname>-validator.pem` (default: lab-validator.pem)

**Service endpoints to check**:
- Chef Automate web interface (https://<hostname>)
- Chef Infra Server API endpoints

**Templates rendered**: None explicitly in the script (Chef Automate handles template rendering internally)

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

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem

# Service health checks
curl -k https://localhost/api/_status
curl -k https://localhost/organizations/lab

# Log verification
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Network listening
sudo netstat -tulpn | grep -E '443|80'
sudo ss -tlnp | grep -E '443|80'

# Resource usage
df -h
free -m
top -n 1
```