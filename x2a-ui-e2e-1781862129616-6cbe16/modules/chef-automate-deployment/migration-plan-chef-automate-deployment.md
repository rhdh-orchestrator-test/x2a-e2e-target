---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed on the local system
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
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flags

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial user with:
     - Username: jtonello
     - Full name: John Tonello
     - Email: jtonello@chef.lab
     - Password: password
     - Saves user key to jtonello.pem
   - Creates organization with:
     - Short name: lab
     - Full name: Chef Lab
     - Associates with created user
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (this is a standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 5 credentials detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Credentials

- **Variable(s)**: `username`, `longusername`, `useremail`, `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Creates the initial admin user for Chef Infra Server

### Chef Organization Credentials

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Creates the initial organization in Chef Infra Server

### Generated PEM Files

- **Variable(s)**: `userfilename`, `orgfilename`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Generated files (jtonello.pem, lab-validator.pem)
- **Usage context**: Authentication keys for Chef Infra Server access

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- jtonello.pem (user key file)
- lab-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hosts | grep automate.chef.lab
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/_status

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test API access with keys
knife user list -s https://localhost/organizations/lab -u jtonello --key jtonello.pem -k

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-automate logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# System resources
df -h
free -m
top -n 1
```