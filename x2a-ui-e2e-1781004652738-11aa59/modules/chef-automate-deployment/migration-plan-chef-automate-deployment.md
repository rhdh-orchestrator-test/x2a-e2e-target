---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: A combined deployment of Chef Automate and Chef Infra Server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI, 9631 for backend services)
  - Key Config: Hostname, user creation, organization creation

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
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the following attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Generates user key file: jtonello.pem
   - Creates a Chef organization with the following attributes:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Generates organization validator key file: lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

Note: The repository also contains a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following the same configuration pattern but with the `--product infra-server` flag instead of both products.

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (script-based deployment)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/v0/health

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl test

# User and organization verification
sudo chef-server-ctl user-list  # Should include 'jtonello' or configured username
sudo chef-server-ctl org-list  # Should include 'lab' or configured organization name

# Key files
ls -la ~/${username}.pem  # Should exist and have proper permissions
ls -la ~/${orgname}-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443  # Chef Automate UI
ss -tlnp | grep 9631  # Chef Automate backend services

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# API access test (requires user key)
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ~/${username}.pem

# Web UI access
curl -k -I https://localhost  # Should return HTTP 200 OK
```