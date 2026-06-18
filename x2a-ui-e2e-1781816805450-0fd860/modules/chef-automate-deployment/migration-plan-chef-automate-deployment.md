---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring hostname, system parameters, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: A single instance of Chef Automate with integrated Chef Infra Server
  - Hostname: Configurable (default: automate.chef.lab)
  - Port: 443
  - Key Config: Configured with default user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA automatically
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with configurable:
     - Username (default: jtonello)
     - Full name (default: John Tonello)
     - Email (default: jtonello@chef.lab)
     - Password (default: password)
     - Saves user key to [username].pem file
   - Creates initial organization with configurable:
     - Organization short name (default: lab)
     - Organization full name (default: Chef Lab)
     - Associates admin user with organization
     - Saves organization validator key to [orgname]-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

Note: The repository also contains a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following the same configuration steps but with a different deployment command.

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

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- [username].pem (user key file)
- [orgname]-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate service status
sudo chef-automate status

# Chef Infra Server service status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Verify key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test Chef Automate UI access
curl -k https://localhost/api/v0/auth/version

# Test Chef Infra Server API access
knife user list -s https://localhost/organizations/lab -k jtonello.pem -u jtonello

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Logs
sudo chef-automate logs

# System resources
df -h
free -m
top -n 1
```