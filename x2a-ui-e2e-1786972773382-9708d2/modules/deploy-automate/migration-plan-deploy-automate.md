---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: deploy-automate

**TLDR**: This is a Bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates a user and organization.

## Service Type and Instances

**Service Type**: Configuration Management Platform (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's server component for configuration management
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **Set hostname** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the value specified in the hostname variable
   - Resources: hostnamectl command (1)

2. **Configure system parameters** (`setup-automate/deploy-automate.sh`):
   - Sets vm.max_map_count=262144 for Elasticsearch
   - Sets vm.dirty_expire_centisecs=20000 for disk I/O optimization
   - Resources: sysctl command (2)

3. **Download and prepare Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads the Chef Automate CLI binary from packages.chef.io
   - Extracts and makes it executable
   - Resources: curl, gunzip, chmod commands (3)

4. **Deploy Chef Automate and Chef Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs the Chef Automate deployment command with both products
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

5. **Create Chef user** (`setup-automate/deploy-automate.sh`):
   - Creates a user in Chef Infra Server with specified credentials
   - Saves the user's private key to a .pem file
   - Resources: chef-server-ctl user-create command (1)

6. **Create Chef organization** (`setup-automate/deploy-automate.sh`):
   - Creates an organization in Chef Infra Server
   - Associates the previously created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl org-create command (1)

## Dependencies

**External cookbook dependencies**: None (this is a Bash script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 4 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create a Chef Infra Server user

### Chef User Private Key

- **Variable(s)**: `userfilename="${username}.pem"`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Generated and saved to file system
- **Usage context**: Authentication key for the Chef Infra Server user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename="${orgname}-validator.pem"`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Generated and saved to file system
- **Usage context**: Authentication key for the Chef organization

### Chef User Email

- **Variable(s)**: `useremail='jtonello@chef.lab'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create a Chef Infra Server user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (for hostname change)
- /proc/sys/vm/max_map_count (for sysctl parameter)
- /proc/sys/vm/dirty_expire_centisecs (for sysctl parameter)
- ./chef-automate (downloaded binary)
- ./${username}.pem (user key file)
- ./${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (this is a Bash script, not a Chef cookbook with templates)

## Pre-flight checks:
```bash
# Hostname check
hostname
cat /etc/hostname

# System parameters check
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate binary check
ls -la ./chef-automate
file ./chef-automate

# Chef Automate status check
sudo ./chef-automate status

# Chef Infra Server status check
sudo chef-server-ctl status

# User and organization check
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files check
ls -la ./jtonello.pem
ls -la ./lab-validator.pem

# Service status
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/organizations/lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail
```