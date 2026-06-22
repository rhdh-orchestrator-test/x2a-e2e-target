---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring system parameters, installing Chef Automate CLI, deploying Chef products, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Single instance deployment
  - Location/Path: Local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Single instance deployment
  - Location/Path: Local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the same deployment

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server products
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with product flags

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
   - Creates organization and associates the admin user
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create commands

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None specified in the script
**System package dependencies**: curl, gunzip (implied by script usage)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 5 credentials detected in 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Authentication Credentials
- **Variable(s)**: `username`, `longusername`, `useremail`, `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial admin user for Chef Automate/Infra Server

### Organization Authentication
- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial organization in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- ./chef-automate (downloaded CLI binary)
- ./${username}.pem (generated user key file)
- ./${orgname}-validator.pem (generated organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**: No templates are explicitly rendered in the script

## Pre-flight checks:
```bash
# System configuration checks
hostname
cat /etc/hosts | grep $(hostname)
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI installation check
ls -la ./chef-automate
./chef-automate version

# Chef Automate and Chef Infra Server service checks
sudo chef-automate status
curl -k https://localhost/api/_status

# User and organization verification
ls -la ./${username}.pem
ls -la ./${orgname}-validator.pem
sudo chef-server-ctl user-list | grep ${username}
sudo chef-server-ctl org-list | grep ${orgname}

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Service status
sudo systemctl status chef-automate
sudo chef-automate service-versions

# Log checks
sudo journalctl -u chef-automate -f
sudo chef-automate logs

# API connectivity test (requires valid token)
# First get a token
TOKEN=$(sudo chef-automate admin-token)
# Then test API access
curl -k -H "api-token: $TOKEN" https://localhost/api/v0/auth/tokens

# Chef Infra Server API check
knife user list -s https://localhost/organizations/${orgname} -k ./${username}.pem -u ${username}
```