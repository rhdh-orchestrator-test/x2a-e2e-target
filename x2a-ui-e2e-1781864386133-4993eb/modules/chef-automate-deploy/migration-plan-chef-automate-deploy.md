---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using bash scripts. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

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

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value using hostnamectl
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl command, file permissions change

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the chef-automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command

4. **User Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a user in Chef Infra Server with:
     - Username, full name, email, and password
     - Generates a user PEM file for API authentication
   - Resources: chef-server-ctl user-create command

5. **Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates an organization in Chef Infra Server
   - Associates the previously created user with the organization
   - Generates an organization validator PEM file
   - Resources: chef-server-ctl org-create command

The alternative script (`setup-automate/deploy-chef-server.sh`) performs similar operations but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires sufficient system resources for Chef Automate and Chef Infra Server

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Infra Server User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `${username}.pem` (User PEM file in the current directory)
- `${orgname}-validator.pem` (Organization validator PEM file in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (uses Chef Automate's built-in templates)

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

# Verify user creation
sudo chef-server-ctl user-list | grep $username
ls -la $userfilename  # Check if user PEM file exists

# Verify organization creation
sudo chef-server-ctl org-list | grep $orgname
ls -la $orgfilename  # Check if organization validator PEM file exists

# Check Chef Automate UI accessibility
curl -k https://localhost

# Check Chef Infra Server API accessibility
curl -k https://localhost/organizations/$orgname

# Check services
sudo systemctl status chef-automate
sudo chef-server-ctl service-list

# Check logs
sudo chef-automate system-logs

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Resource usage
free -m
df -h
top -n 1
```