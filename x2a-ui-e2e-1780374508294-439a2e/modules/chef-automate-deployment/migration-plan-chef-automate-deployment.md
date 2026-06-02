---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads and installs Chef Automate CLI, deploys the products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Automate, shares same user/org configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flags

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
   - Creates organization and associates the admin user
   - Generates and saves user and organization PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The `deploy-chef-server.sh` script follows a similar pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (standalone deployment script)
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None (this is the initial deployment)

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Chef Admin User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated during deployment and saved to file
- **Usage context**: Authentication key for the admin user

### Chef Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated during deployment and saved to file
- **Usage context**: Authentication key for the organization validator

### Chef Automate License Agreement

- **Variable(s)**: `--accept-terms-and-mlsa=true`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Acceptance of Chef Automate license terms

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `~/${username}.pem` (admin user PEM file)
- `~/${orgname}-validator.pem` (organization validator PEM file)
- Chef Automate configuration files (in default installation path)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: No templates are rendered directly by these scripts

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
which chef-automate
chef-automate version

# Chef Automate and Chef Infra Server status
sudo chef-automate status
curl -k https://localhost/api/v0/health

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# PEM files
ls -la ~/$userfilename
ls -la ~/$orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
sudo systemctl status chef-automate
sudo chef-automate service-versions

# Log verification
sudo chef-automate logs deployment
sudo journalctl -u chef-automate

# API connectivity test
curl -k https://localhost/api/v0/auth/version
```