---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the hostname to the configured value using hostnamectl
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials
   - Creates a Chef organization
   - Associates the user with the organization
   - Generates and saves authentication key files
   - Resources: chef-server-ctl commands (2)

## Dependencies

**External dependencies**: None specified in the script
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 5 credentials detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the Chef user account

### Chef User Authentication Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated and saved to local file system
- **Usage context**: Authentication key for the Chef user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated and saved to local file system
- **Usage context**: Authentication key for the Chef organization

### Chef User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used for Chef user creation

### Chef User Full Name

- **Variable(s)**: `longusername`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used for Chef user creation

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `${username}.pem` (user authentication key)
- `${orgname}-validator.pem` (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None explicitly rendered in the script

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# Authentication key verification
ls -la $userfilename
ls -la $orgfilename

# Web UI accessibility
curl -k https://localhost

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service processes
ps aux | grep chef-automate
ps aux | grep chef-server

# Logs
sudo journalctl -u chef-automate -f
sudo journalctl -u chef-server -f

# API connectivity test (requires the user key)
knife user list -s https://localhost/organizations/$orgname -u $username -k $userfilename

# System resources
df -h
free -m
top -n 1
```