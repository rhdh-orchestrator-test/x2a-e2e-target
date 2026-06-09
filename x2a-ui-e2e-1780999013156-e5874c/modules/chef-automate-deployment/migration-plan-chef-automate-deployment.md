---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script deployment of Chef Automate and Chef Infra Server. It configures a single instance with system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Deployed with `--product automate` flag

- **Chef Infra Server**: 
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Deployed with `--product infra-server` flag, creates initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system settings:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server with a single command
   - Accepts terms and MLSA automatically
   - Resources: chef-automate deploy command with flags

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Saves user key to a .pem file
   - Creates initial organization with:
     - Organization short name (default: 'lab')
     - Organization full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (this is a bash script)
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
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User and Organization Keys

- **Variable(s)**: `userfilename="${username}.pem"`, `orgfilename="${orgname}-validator.pem"`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated files
- **Usage context**: Authentication keys for Chef user and organization validator

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- chef-automate executable in the current directory
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (this is a bash script)

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

# Verify Chef Automate UI is accessible
curl -k https://localhost/api/v0/auth/version

# Verify Chef Infra Server is accessible
curl -k https://localhost/organizations

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Verify PEM files exist and have content
ls -la jtonello.pem
ls -la lab-validator.pem

# Check listening ports
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Check Chef Automate logs
sudo journalctl -u chef-automate

# Check Chef Infra Server logs
sudo chef-server-ctl tail

# Verify Chef Automate services
sudo chef-automate service-versions

# Memory usage
free -m
ps aux | grep chef | sort -k 4 -r | head -10
```