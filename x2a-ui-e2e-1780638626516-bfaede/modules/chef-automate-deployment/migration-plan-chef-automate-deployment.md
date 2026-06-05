---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: A combined deployment of Chef Automate and Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (Chef Server typically uses 443)
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
   - Creates initial admin user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial organization:
     - Organization short name: lab (configurable)
     - Organization full name: Chef Lab (configurable)
     - Associates admin user with organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

Note: The repository also contains a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following the same configuration steps but with a different deployment command.

## Dependencies

**External cookbook dependencies**: None (this is a standalone deployment script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial admin user in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User key file (jtonello.pem by default)
- Organization validator key file (lab-validator.pem by default)

**Service endpoints to check**:
- Ports listening: 443 (Chef Infra Server HTTPS)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (this is a deployment script, not a Chef cookbook with templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list  # Should include 'jtonello' or configured username
sudo chef-server-ctl user-show jtonello  # Replace with configured username

# Verify organization creation
sudo chef-server-ctl org-list  # Should include 'lab' or configured org name
sudo chef-server-ctl org-show lab  # Replace with configured org name

# Verify key files
ls -la jtonello.pem  # Replace with configured username
ls -la lab-validator.pem  # Replace with configured org name

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service health check
curl -k https://localhost/_status  # Basic Chef Server health check

# Log verification
sudo journalctl -u chef-server  # Check Chef Server logs
sudo journalctl -u automate  # Check Chef Automate logs

# Chef Server API test (requires properly configured knife)
knife user list  # Should show the created user
knife client list  # Should show the validator client
```