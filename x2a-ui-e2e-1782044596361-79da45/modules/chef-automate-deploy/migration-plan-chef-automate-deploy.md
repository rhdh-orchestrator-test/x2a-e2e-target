---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
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
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial organization
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the admin user with the organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- jtonello.pem (user key file)
- lab-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should return automate.chef.lab
cat /proc/sys/vm/max_map_count  # Should return 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should return 20000

# Chef Automate CLI
which chef-automate
chef-automate version

# Chef Automate service status
sudo chef-automate status

# Chef Infra Server service status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list  # Should include jtonello
ls -la jtonello.pem  # Verify user key exists

# Verify organization creation
sudo chef-server-ctl org-list  # Should include lab
ls -la lab-validator.pem  # Verify organization validator key exists

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443
curl -k https://localhost  # Should return Chef Automate login page

# Logs
sudo chef-automate logs

# System resources
df -h  # Check disk space
free -m  # Check memory usage
top -n 1  # Check CPU usage
```