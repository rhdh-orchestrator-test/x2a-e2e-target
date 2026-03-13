# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of Bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port: 443 (HTTPS)
  - Key Config: Deployed with `--product automate` flag
  
- **Chef Infra Server**:
  - Location/Path: Installed via Chef Automate CLI
  - Port: 443 (HTTPS)
  - Key Config: Deployed with `--product infra-server` flag
  - User: Single admin user created (configurable via variables)
  - Organization: Single organization created (configurable via variables)

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of Bash scripts that perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using `hostnamectl set-hostname $hostname`
   - Configures kernel parameters for optimal performance:
     - Sets `vm.max_map_count=262144`
     - Sets `vm.dirty_expire_centisecs=20000`
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates admin user with `chef-server-ctl user-create`
     - User attributes: username, full name, email, password
     - Saves user key to `$username.pem` file
   - Creates organization with `chef-server-ctl org-create`
     - Organization attributes: short name, full name
     - Associates admin user with organization
     - Saves organization validator key to `$orgname-validator.pem` file
   - Resources: chef-server-ctl (2)

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (self-contained scripts)
**System package dependencies**: curl, gunzip (typically pre-installed)
**Service dependencies**: None (scripts install the services)

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `$username.pem` (Admin user key file)
- `$orgname-validator.pem` (Organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI)
- Network interfaces: All interfaces (0.0.0.0) or specific IP if configured

**Templates rendered**: No templates are used in these scripts

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate service status
sudo chef-automate status

# Chef Infra Server service status
sudo chef-server-ctl status

# Chef Automate API check
curl -k https://localhost/api/v0/auth/version

# Chef Infra Server API check
curl -k https://localhost/organizations

# User verification
sudo chef-server-ctl user-list | grep $username
ls -la $username.pem

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
ls -la $orgname-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Logs
sudo chef-automate system-logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# Configuration validation
sudo chef-automate config show
```