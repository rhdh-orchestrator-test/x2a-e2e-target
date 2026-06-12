---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: A single instance deployment of Chef Automate with Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI, 9631 for backend services)
  - Key Config: Hostname, user account, organization name

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
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial organization:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates admin user with organization
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

Note: The repository also contains a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following the same configuration pattern but with the `--product infra-server` flag only.

## Dependencies

**External cookbook dependencies**: None (this is a standalone deployment script)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: This password is used for the initial Chef admin user account creation

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml
- /etc/opscode/chef-server.rb
- User key file: jtonello.pem (in current directory)
- Organization validator key: lab-validator.pem (in current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://automate.chef.lab/api/v0/auth/version

# Chef Infra Server API access
curl -k https://localhost/organizations
curl -k https://automate.chef.lab/organizations

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test API access with keys
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem

# Logs
sudo chef-automate system-logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Process verification
ps aux | grep chef
ps aux | grep automate

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/opscode
```