---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script deployment of Chef Automate and Chef Infra Server. It configures hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
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
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server integration
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
     - Username: configured value (default: 'jtonello')
     - Full name: configured value (default: 'John Tonello')
     - Email: configured value (default: 'jtonello@chef.lab')
     - Password: configured value (default: 'password')
     - Saves user key to file: username.pem
   - Creates initial organization
     - Short name: configured value (default: 'lab')
     - Full name: configured value (default: 'Chef Lab')
     - Associates admin user with organization
     - Saves organization validator key to file: orgname-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

Note: The repository also contains a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following a similar process but with the `--product infra-server` flag only.

## Dependencies

**External cookbook dependencies**: None (this is a standalone bash script)
**System package dependencies**: curl, gunzip, sudo
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
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ~/{username}.pem (user key file)
- ~/{orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/_status

# Chef Infra Server API access
knife user list -s https://localhost/organizations/lab -k ~/jtonello.pem -u jtonello

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
```