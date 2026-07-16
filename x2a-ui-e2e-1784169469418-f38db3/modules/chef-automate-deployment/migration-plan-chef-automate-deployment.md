---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA automatically

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
   - Sets configuration variables for deployment:
     - hostname: 'automate.chef.lab'
     - username: 'jtonello'
     - longusername: 'John Tonello'
     - useremail: 'jtonello@chef.lab'
     - userpassword: 'password'
     - orgname: 'lab'
     - longorgname: 'Chef Lab'
   - Sets dynamic variables:
     - userfilename: "${username}.pem"
     - orgfilename: "${orgname}-validator.pem"
   - Resources: Variable declarations (9)

2. **Configure System** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command (1), sysctl commands (2)

3. **Download Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes it executable
   - Resources: curl command (1), chmod command (1)

4. **Deploy Chef Automate and Chef Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs Chef Automate deployment with both products
   - Accepts terms and MLSA automatically
   - Resources: chef-automate deploy command (1)

5. **Create User and Organization** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials
   - Creates a Chef organization
   - Associates the user with the organization
   - Saves authentication keys to files
   - Resources: chef-server-ctl user-create command (1), chef-server-ctl org-create command (1)

## Dependencies

**External cookbook dependencies**: None (this is a bash script, not a Chef cookbook)
**System package dependencies**: curl, sudo, hostnamectl, sysctl
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
- ${username}.pem (user authentication key)
- ${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (this is a bash script that doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should return automate.chef.lab
sysctl vm.max_map_count  # Should return vm.max_map_count = 262144
sysctl vm.dirty_expire_centisecs  # Should return vm.dirty_expire_centisecs = 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should show executable file
./chef-automate version  # Should show version information

# Chef Automate status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/status  # Should return status JSON

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include jtonello
sudo chef-server-ctl org-list  # Should include lab

# Authentication key files
ls -la jtonello.pem  # Should show user key file
ls -la lab-validator.pem  # Should show organization validator key file

# Network listening
sudo netstat -tulpn | grep LISTEN  # Should show services listening on ports
sudo ss -tulpn | grep LISTEN  # Alternative to netstat

# Web UI access
curl -k https://localhost  # Should redirect to login page
curl -k -I https://localhost  # Should return HTTP 200 or 302

# Logs
sudo journalctl -u chef-automate -n 50  # Check Chef Automate logs
sudo chef-automate logs  # Alternative way to check logs

# Disk space
df -h  # Check available disk space
```