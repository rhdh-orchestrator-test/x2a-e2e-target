---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring system parameters, installing Chef Automate CLI, deploying Chef products, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Main Chef Automate server instance
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef server instance
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (typically 443)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server products
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Generates user key file: jtonello.pem
   - Creates organization:
     - Org short name: lab (configurable)
     - Org full name: Chef Lab (configurable)
     - Associates with created user
     - Generates organization validator key: lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for hostname configuration

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
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- chef-automate executable in current directory
- User key file: jtonello.pem (or configured username)
- Organization validator key: lab-validator.pem (or configured org name)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration checks
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate installation checks
ls -la ./chef-automate
./chef-automate version

# Chef Automate service checks
sudo chef-automate status
curl -k https://localhost/api/v0/status

# Chef Infra Server checks
sudo chef-server-ctl status
sudo chef-server-ctl test

# User and organization checks
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab
ls -la jtonello.pem
ls -la lab-validator.pem

# Verify connectivity with knife
knife ssl fetch -s https://localhost
knife ssl check -s https://localhost
knife user list -s https://localhost -k jtonello.pem -u jtonello
knife org list -s https://localhost -k jtonello.pem -u jtonello

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Chef Automate UI access
curl -k https://localhost/api/v0/auth/version
```