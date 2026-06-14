---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup. The main features include system tuning, downloading and installing Chef Automate CLI, deploying Chef products, and creating initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **chef-automate**: Chef Automate server with integrated Chef Infra Server
  - Location/Path: Local system (hostname configured via script)
  - Port/Socket: Default ports (443 for web UI, 9631 for backend services)
  - Key Config: System tuning parameters (vm.max_map_count=262144, vm.dirty_expire_centisecs=20000)

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Tunes kernel parameters for optimal performance:
     - Sets vm.max_map_count=262144 (required for Elasticsearch)
     - Sets vm.dirty_expire_centisecs=20000 (improves I/O performance)
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial Chef user with specified attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial Chef organization:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates with created user
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate has internal dependencies on PostgreSQL, Elasticsearch, and other services that are managed by the deployment process

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef/jtonello.pem (user key file)
- /etc/chef/lab-validator.pem (organization validator key file)
- /etc/systemd/system/chef-automate.service (service file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI), 9631 (Chef Automate backend)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None explicitly rendered by the script. Chef Automate handles its own template rendering internally.

## Pre-flight checks:

```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate service status
sudo systemctl status chef-automate
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user and organization
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Check key files
ls -la /etc/chef/jtonello.pem
ls -la /etc/chef/lab-validator.pem

# Test API access
curl -k https://localhost/api/_status

# Test knife commands with the created user
knife user list -s https://localhost/organizations/lab -u jtonello -k /etc/chef/jtonello.pem

# Network listening
sudo netstat -tulpn | grep -E '443|9631'
sudo ss -tlnp | grep -E '443|9631'

# Logs
sudo journalctl -u chef-automate -f
sudo chef-automate system-logs

# Verify web UI access
curl -k -I https://localhost/

# Check disk space
df -h /var/opt/chef-automate
```