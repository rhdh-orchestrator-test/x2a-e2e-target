---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server products, and creates an initial user and organization.

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
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod (3)

3. **Chef Automate and Chef Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial organization with:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the admin user with the organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires network connectivity to download Chef packages

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- chef-automate executable in the current directory
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname (e.g., automate.chef.lab)
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la chef-automate  # Should exist and be executable
./chef-automate version  # Should return version information

# Chef Automate and Chef Infra Server
curl -k https://localhost/api/v0/status  # Should return status information for Chef Automate
curl -k https://localhost/organizations  # Should return organizations for Chef Infra Server

# User and organization verification
ls -la jtonello.pem  # Should exist and be readable
ls -la lab-validator.pem  # Should exist and be readable

# Service status
sudo chef-automate status  # Should show all services running
sudo chef-server-ctl status  # Should show all Chef Infra Server services running

# Network listening
sudo netstat -tulpn | grep LISTEN | grep ':443'  # Should show services listening on port 443
sudo ss -tulpn | grep ':443'  # Alternative check for services listening on port 443

# Logs
sudo chef-automate logs  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs

# Web UI access
curl -k -I https://localhost  # Should return HTTP 200 OK for Chef Automate UI
```