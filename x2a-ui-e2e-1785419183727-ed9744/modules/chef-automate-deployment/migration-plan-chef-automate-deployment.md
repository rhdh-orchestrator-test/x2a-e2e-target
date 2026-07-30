---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using bash scripts. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
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

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial organization
     - Org short name: lab (configurable)
     - Org full name: Chef Lab (configurable)
     - Associates admin user with organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same process but only deploys the Chef Infra Server product without Chef Automate.

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

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Infra Server configuration directory)
- User and organization PEM files in the current directory:
  - jtonello.pem (or custom username.pem)
  - lab-validator.pem (or custom orgname-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (uses Chef Automate's built-in templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/status  # Should return status information

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization

# Verify PEM files
ls -la *.pem  # Should show user and organization PEM files
openssl rsa -in jtonello.pem -check  # Verify user key is valid (replace with actual filename)
openssl rsa -in lab-validator.pem -check  # Verify org validator key is valid (replace with actual filename)

# Network listening
sudo netstat -tulpn | grep ':443'  # Should show Chef Automate/Infra Server listening
sudo ss -tlnp | grep ':443'  # Alternative check for listening ports

# Web UI access
curl -k -I https://localhost  # Should return HTTP 200 OK for Chef Automate UI

# API access
curl -k -H "Content-Type: application/json" https://localhost/organizations  # Should return organizations list

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate system-logs  # View Chef Automate system logs

# Service status
systemctl status chef-automate  # Check Chef Automate service status
```