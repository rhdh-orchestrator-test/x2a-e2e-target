---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring system parameters, installing Chef Automate CLI, deploying Chef Automate and Chef Infra Server, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

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

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username: configured value (default: 'jtonello')
     - Full name: configured value (default: 'John Tonello')
     - Email: configured value (default: 'jtonello@chef.lab')
     - Password: configured value (default: 'password')
     - Saves user key to a PEM file
   - Creates a Chef organization with:
     - Short name: configured value (default: 'lab')
     - Full name: configured value (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same process but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: This password is used for creating the initial Chef user account that will have administrative access to the Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`
- `/etc/chef/`
- User PEM file (default: `jtonello.pem`)
- Organization validator PEM file (default: `lab-validator.pem`)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Service status
sudo chef-automate status  # Check Chef Automate status
sudo chef-server-ctl status  # Check Chef Infra Server status

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# File verification
ls -la jtonello.pem  # Verify user key file exists
ls -la lab-validator.pem  # Verify organization validator key exists

# Network listening
sudo netstat -tulpn | grep 443  # Verify Chef Automate/Infra Server is listening on port 443
sudo ss -tlnp | grep 443  # Alternative check for listening ports

# Web UI access
curl -k https://localhost/api/v0/health  # Check Chef Automate API health
curl -k https://localhost/_status  # Check Chef Infra Server status endpoint

# Log verification
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs

# Authentication test
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Test API access with the created user
```