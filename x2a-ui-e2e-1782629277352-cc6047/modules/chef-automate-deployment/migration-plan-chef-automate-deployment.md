---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (typically 443)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **Set Variables** (`setup-automate/deploy-automate.sh`):
   - Defines configuration variables for deployment:
     - hostname: 'automate.chef.lab'
     - username: 'jtonello'
     - longusername: 'John Tonello'
     - useremail: 'jtonello@chef.lab'
     - userpassword: 'password'
     - orgname: 'lab'
     - longorgname: 'Chef Lab'
   - Defines dynamic variables:
     - userfilename: "${username}.pem"
     - orgfilename: "${orgname}-validator.pem"
   - Resources: Variable definitions (9)

2. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command (1), sysctl commands (2)

3. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl command (1), file permission change (1)

4. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server with one command
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

5. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a user with chef-server-ctl:
     - Username: jtonello
     - Full name: John Tonello
     - Email: jtonello@chef.lab
     - Password: password
     - Saves user key to jtonello.pem
   - Creates an organization with chef-server-ctl:
     - Short name: lab
     - Full name: Chef Lab
     - Associates with user jtonello
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl commands (2)

## Dependencies

**External cookbook dependencies**: None (this is a bash script, not a Chef cookbook)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined in the script

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
- ${username}.pem (jtonello.pem by default)
- ${orgname}-validator.pem (lab-validator.pem by default)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (this is a bash script that doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should return automate.chef.lab
sysctl vm.max_map_count  # Should return vm.max_map_count = 262144
sysctl vm.dirty_expire_centisecs  # Should return vm.dirty_expire_centisecs = 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should show the executable file
./chef-automate version  # Should show version information

# Chef Automate and Chef Infra Server status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/health  # Should return health status

# Chef Server functionality
sudo chef-server-ctl status  # Should show all services running
ls -la jtonello.pem  # Should show the user key file
ls -la lab-validator.pem  # Should show the organization validator key file

# User and organization verification
sudo chef-server-ctl user-list  # Should include jtonello
sudo chef-server-ctl org-list  # Should include lab

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep 443  # Alternative to check listening ports

# Logs
sudo chef-automate logs  # Check Chef Automate logs
sudo journalctl -u chef-automate  # Check systemd logs for Chef Automate

# Web UI access
curl -k https://automate.chef.lab/api/v0/auth/version  # Should return version info
```