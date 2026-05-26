---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value using `hostnamectl`
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value using `hostnamectl`
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization with the specified name and associates the user
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hosts` (hostname should be set)
- `$userfilename` (user PEM file, default: jtonello.pem)
- `$orgfilename` (organization validator PEM file, default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

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

# Verify PEM files
ls -la $userfilename
ls -la $orgfilename

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/organizations/$orgname

# Log verification
sudo journalctl -u chef-automate
sudo chef-automate logs

# Service health check
sudo chef-automate service-versions
sudo chef-server-ctl service-list

# Verify Chef Server API access using the generated PEM file
knife user list -s https://localhost/organizations/$orgname -u $username -k $userfilename

# Verify Chef Automate UI is accessible
curl -k https://localhost
```