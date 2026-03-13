# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two Bash scripts that deploy Chef Automate and Chef Infra Server. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef infrastructure
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with hostname, user settings, and organization settings

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with hostname, user settings, and organization settings

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA (Master License and Services Agreement)
   - Resources: chef-automate deploy command with --product flags

4. **Chef Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Saves the user's private key to a .pem file
   - Creates a Chef organization with the configured organization name
   - Associates the created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl user-create and chef-server-ctl org-create commands

## Dependencies

**External cookbook dependencies**: None (standalone scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User private key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)
- Chef Automate CLI binary (chef-automate)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UIs)
- Network interfaces: All interfaces (0.0.0.0) or specific IP if configured

**Templates rendered**:
- No templates are explicitly rendered in these scripts

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la chef-automate  # Should exist and be executable
./chef-automate version  # Should return version information

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the created user
ls -la jtonello.pem  # Should exist and contain private key

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization
ls -la lab-validator.pem  # Should exist and contain validator key

# Network listening
netstat -tulpn | grep 443  # Should show services listening on port 443
ss -tlnp | grep 443  # Alternative to netstat

# Web UI access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/_status  # Should return status information

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate service logs
sudo chef-automate system-logs  # View Chef Automate system logs

# Service health
sudo chef-automate service-versions  # Check versions of deployed services
sudo chef-automate status  # Check status of all Chef Automate services
```