---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module consists of a Bash script that deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys Automate and Infra Server products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **Set System Variables** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the value specified in the script (default: 'automate.chef.lab')
   - Defines user variables: username, longusername, useremail, userpassword
   - Defines organization variables: orgname, longorgname
   - Resources: Bash variables (7)

2. **Configure System Settings** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl (1), sysctl (2)

3. **Download and Install Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl (1), file permissions (1)

4. **Deploy Chef Automate and Chef Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs chef-automate deploy command with:
     - --product automate
     - --product infra-server
     - --accept-terms-and-mlsa=true
   - Resources: chef-automate CLI (1)

5. **Create Initial User** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Saves user key to a .pem file
   - Resources: chef-server-ctl (1)

6. **Create Initial Organization** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates the previously created user
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should return 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should return 20000

# Chef Automate CLI installation
which chef-automate
chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list  # Should include the created user
ls -la jtonello.pem  # Or the configured username.pem file

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization
ls -la lab-validator.pem  # Or the configured orgname-validator.pem file

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/auth/version  # Should return Chef Automate API version
curl -k https://localhost/_status  # Should return Chef Infra Server status

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Service health
sudo chef-automate status
sudo chef-server-ctl status
```