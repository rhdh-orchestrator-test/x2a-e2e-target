---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a Linux system. It configures system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Deployed with Chef Infra Server integration

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate, configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial organization:
     - Org short name: lab (configurable)
     - Org full name: Chef Lab (configurable)
     - Associates admin user with organization
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

The `deploy-chef-server.sh` script follows a similar pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: This credential is used to set the initial password for the Chef Infra Server admin user

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/opscode/
- User key file: jtonello.pem (or configured username)
- Organization validator key: lab-validator.pem (or configured org name)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**: None explicitly rendered in the scripts

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
sudo chef-server-ctl user-list  # Should include the configured username (jtonello)
sudo chef-server-ctl org-list  # Should include the configured org name (lab)

# Key files
ls -la jtonello.pem  # Should exist and have proper permissions
ls -la lab-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443  # Should show services listening on port 443
ss -tlnp | grep 443  # Alternative to check port 443

# Web UI access
curl -k https://localhost  # Should return Chef Automate UI content
curl -k https://localhost/_status  # Should return status information

# API access
curl -k https://localhost/organizations/lab  # Should return organization info when authenticated

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs

# Disk space
df -h /var/opt/chef-automate  # Check disk space for Chef Automate
df -h /var/opt/opscode  # Check disk space for Chef Infra Server
```