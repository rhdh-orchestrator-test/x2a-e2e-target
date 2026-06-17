---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a single instance of Chef Automate with integrated Chef Infra Server, configures system parameters, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Infra Server

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Associated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with integrated Chef Infra Server
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
   - Creates organization and associates the admin user
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None (this script installs the services)

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostnamectl (hostname configuration)
- /etc/sysctl.conf or /etc/sysctl.d/* (kernel parameter settings)
- Generated PEM files: <username>.pem and <orgname>-validator.pem

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate service status
sudo chef-automate status

# Chef Infra Server service status
sudo chef-server-ctl status

# Verify Chef Automate UI is accessible
curl -k https://localhost/api/v0/auth/version  # Should return version info
curl -k https://localhost  # Should return 200 OK

# Verify Chef Infra Server API is accessible
curl -k https://localhost/organizations  # Should return 401 (authentication required)

# Verify user and organization
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# Verify PEM files exist and have correct permissions
ls -la ${username}.pem  # Should exist and be readable
ls -la ${orgname}-validator.pem  # Should exist and be readable

# Test authentication with the created user
knife user list -s https://localhost -u ${username} -k ${username}.pem  # Should succeed

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-automate logs

# System resources
df -h  # Check disk space
free -m  # Check memory usage
top -n 1  # Check CPU usage
```