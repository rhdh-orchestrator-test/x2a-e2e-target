---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This repository contains two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up a Chef server environment with user and organization configuration. There is no actual Chef cookbook structure or chef_deployment module in this repository.

## Service Type and Instances

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate and Chef Infra Server**: A single instance deployment of Chef Automate with Chef Infra Server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (Chef Server typically uses 443)
  - Key Config: Creates a user and organization with associated PEM files

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The repository contains two bash scripts that deploy Chef Automate and Chef Infra Server:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate with Chef Infra Server using the CLI
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for the user and organization validator

2. **deploy-chef-server.sh**:
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server using the CLI
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for the user and organization validator

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on Chef Automate CLI)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- User PEM file: `<username>.pem` (default: jtonello.pem)
- Organization validator PEM file: `<orgname>-validator.pem` (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Server HTTPS)
- Network interfaces: All interfaces by default

**Templates rendered**: None (no Chef templates in this repository)

## Pre-flight checks:
```bash
# Check if Chef Automate is running
sudo chef-automate status

# Check if Chef Infra Server is running
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Check if PEM files exist
ls -la jtonello.pem
ls -la lab-validator.pem

# Test Chef Server API access
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem

# Check system settings
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check hostname configuration
hostname

# Check network connectivity
curl -k https://automate.chef.lab

# Check Chef Automate UI access (if deployed)
curl -k https://automate.chef.lab
```