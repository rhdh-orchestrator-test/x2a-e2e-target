---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: A single instance of Chef Automate with integrated Chef Infra Server
  - Location/Path: Deployed on the local system
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
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI tool
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified parameters:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Generates user key file: jtonello.pem
   - Creates initial organization with specified parameters:
     - Organization short name: lab (configurable)
     - Organization full name: Chef Lab (configurable)
     - Associates the admin user with the organization
     - Generates organization validator key: lab-validator.pem
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

Note: The repository also contains a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following a similar process but with the `--product infra-server` flag only.

## Dependencies

**External cookbook dependencies**: None (this is a standalone deployment script)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the deployment script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: This credential is used as the password for the initial Chef admin user created during deployment

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- /etc/opscode/ (Chef Server configuration directory)
- User key file: jtonello.pem (or configured username)
- Organization validator key: lab-validator.pem (or configured organization name)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI)
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

# Chef Automate UI access
curl -k https://localhost/api/v0/auth/version  # Should return version information
curl -k https://localhost  # Should return Chef Automate UI HTML

# Chef Server API access
curl -k https://localhost/organizations  # Should return organizations list

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# Key files
ls -la jtonello.pem  # Should exist and have proper permissions (or configured username)
ls -la lab-validator.pem  # Should exist and have proper permissions (or configured org name)

# Network listening
netstat -tulpn | grep ':443'  # Should show Chef Automate listening
ss -tlnp | grep ':443'  # Alternative check for Chef Automate listening

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
sudo chef-server-ctl tail

# Deployment verification
sudo chef-automate verify
```