---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: A single instance deployment of Chef Automate with Chef Infra Server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI, 9631 for backend services)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Generates user key file: jtonello.pem
   - Creates initial organization:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates admin user with organization
     - Generates organization validator key: lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

Note: The repository also contains a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following the same configuration pattern but with the `--product infra-server` flag only.

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword` (set to 'password')
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Infra Server configuration directory)
- User key file: jtonello.pem (or configured username)
- Organization validator key: lab-validator.pem (or configured organization)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for web UI), 9631 (Chef Automate backend services)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate API and UI
curl -k https://localhost/api/v0/auth/version  # Should return version info
curl -k https://localhost  # Should return the Chef Automate UI HTML

# Chef Infra Server API
curl -k https://localhost/organizations  # Should return organizations list

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization

# Key files
ls -la jtonello.pem  # Or configured username.pem
ls -la lab-validator.pem  # Or configured organization-validator.pem

# Network listening
sudo netstat -tulpn | grep -E '443|9631'
sudo ss -tlnp | grep -E '443|9631'

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
sudo chef-server-ctl tail

# Deployment verification
sudo chef-automate verify
```