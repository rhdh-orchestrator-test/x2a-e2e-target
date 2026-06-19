---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a single VM. It configures system settings, downloads and installs Chef Automate CLI, deploys the Chef Automate and Infra Server products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: Deployed with Chef Infra Server integration

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname using `hostnamectl set-hostname`
   - Configures kernel parameters for optimal performance:
     - Sets `vm.max_map_count=262144` for Elasticsearch
     - Sets `vm.dirty_expire_centisecs=20000` for disk write performance
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA (Master License and Services Agreement)
   - Resources: chef-automate deploy command with --product flags

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates an initial admin user with specified credentials
   - Creates an organization and associates the admin user
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None (this script installs the services)

## Credentials

**Detection Summary**: 5 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef admin user

### Chef Admin User Information

- **Variable(s)**: `username`, `longusername`, `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef admin user

### Chef Organization Information

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef organization

### User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated during execution, saved to file
- **Usage context**: Authentication key for the Chef admin user

### Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated during execution, saved to file
- **Usage context**: Authentication key for the Chef organization

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `${userfilename}` (User PEM file in current directory)
- `${orgfilename}` (Organization validator PEM file in current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
which chef-automate
chef-automate version

# Service status
sudo chef-automate status
systemctl status chef-automate

# Chef Infra Server status
sudo chef-server-ctl status
systemctl status chef-server

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured orgname

# PEM files
ls -la ${username}.pem  # Should exist and have proper permissions
ls -la ${orgname}-validator.pem  # Should exist and have proper permissions

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web interface accessibility
curl -k https://localhost/api/v0/status  # Should return Chef Automate status
curl -k https://localhost/_status  # Should return Chef Infra Server status

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Disk space
df -h /  # Ensure sufficient disk space (Chef Automate requires at least 40GB)
df -h /var  # Ensure sufficient disk space for logs and data

# Memory usage
free -m  # Ensure sufficient memory (Chef Automate requires at least 16GB RAM)
```