---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization settings

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads the Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Resources: curl command, file permissions change

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate CLI command

4. **Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate CLI command

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user in Chef Infra Server with the following attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
   - Saves user key to a PEM file (jtonello.pem)
   - Resources: chef-server-ctl user-create command

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an organization in Chef Infra Server:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
   - Associates the previously created user with the organization
   - Saves organization validator key to a PEM file (lab-validator.pem)
   - Resources: chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None (this script installs Chef Automate and Chef Infra Server)

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: This password is used for the initial admin user created in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- User PEM file (jtonello.pem)
- Organization validator PEM file (lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname (automate.chef.lab)
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la chef-automate  # Should exist and be executable

# Chef Automate and Chef Infra Server status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/auth/version  # Should return Chef Automate API version
curl -k https://localhost/organizations  # Should return Chef Infra Server organizations

# User and organization verification
ls -la jtonello.pem  # Should exist
ls -la lab-validator.pem  # Should exist

# Test user authentication
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem  # Should list users including jtonello

# Test organization access
knife org list -s https://localhost -u jtonello -k jtonello.pem  # Should list organizations including lab

# Service status
sudo systemctl status chef-automate  # Should be active
sudo chef-automate service-versions  # Should list all service versions

# Network listening
sudo netstat -tulpn | grep ':443'  # Should show services listening on port 443
sudo ss -tlnp | grep ':443'  # Alternative check for port 443

# Logs
sudo chef-automate logs  # Check for any errors in logs
```