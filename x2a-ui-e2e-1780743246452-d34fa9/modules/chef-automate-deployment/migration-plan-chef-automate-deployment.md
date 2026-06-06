---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in one script, standalone in the other

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl command, file permissions change

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flags

4. **Chef Infra Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server (without Automate) using the Chef Automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Creates a Chef organization with the configured organization name
   - Associates the created user with the organization
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 5 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

### Chef User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef user

### Chef Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef organization

### Chef User Email

- **Variable(s)**: `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Email address for the Chef user account

### Chef MLSA Agreement

- **Variable(s)**: `--accept-terms-and-mlsa=true`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Acceptance of Chef's Master License and Services Agreement

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user PEM file)
- ~/${orgname}-validator.pem (organization validator PEM file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are explicitly rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
which chef-automate
chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://automate.chef.lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
journalctl -u chef-automate -f

# Logs
sudo chef-automate logs

# API connectivity (using the PEM file)
knife user list -s https://automate.chef.lab/organizations/lab -k ~/jtonello.pem -u jtonello

# System resources
df -h
free -m
top -n 1
```