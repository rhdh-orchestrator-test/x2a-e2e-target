# Migration Plan: setup-automate

**TLDR**: This repository contains shell scripts for deploying Chef Automate and Chef Infra Server. There is no actual Chef cookbook structure with recipes, attributes, or templates. The scripts set up Chef infrastructure components using the Chef Automate CLI.

## Service Type and Instances

**Service Type**: Infrastructure Management Platform

**Configured Instances**:
- **Chef Automate**: A platform for infrastructure automation
  - Location/Path: Deployed on the local system
  - Port/Socket: Default Chef Automate ports (443)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default Chef Server ports (443)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

There are no Chef cookbook files (recipes, providers, templates, attributes) in this repository. The repository consists of shell scripts that deploy Chef Automate and Chef Infra Server.

## Module Explanation

The repository contains two shell scripts that perform the following operations:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a Chef user with the configured username, name, email, and password
   - Creates a Chef organization and associates the user with it
   - Generates user and organization PEM files

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Chef Automate
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal Chef Server performance
   - Downloads the Chef Automate CLI
   - Deploys only Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a Chef user with the configured username, name, email, and password
   - Creates a Chef organization and associates the user with it
   - Generates user and organization PEM files

Both scripts use the following configurable variables:
- hostname: The hostname for the Chef server (default: 'automate.chef.lab')
- username: Chef user's username (default: 'jtonello')
- longusername: Chef user's full name (default: 'John Tonello')
- useremail: Chef user's email (default: 'jtonello@chef.lab')
- userpassword: Chef user's password (default: 'password')
- orgname: Chef organization short name (default: 'lab')
- longorgname: Chef organization full name (default: 'Chef Lab')

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (Chef Automate CLI handles dependencies)
**Service dependencies**: None explicitly configured

## Checks for the Migration

**Files to verify**:
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)
- Chef Automate configuration files (created by the deployment process)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server)
- Network interfaces: All interfaces or as configured by Chef Automate

**Templates rendered**: None (no Chef templates in this repository)

## Pre-flight checks:
```bash
# System hostname check
hostname
hostnamectl

# System parameters check
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Chef user verification
sudo chef-server-ctl user-list | grep jtonello

# Chef organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files existence check
ls -la jtonello.pem
ls -la lab-validator.pem

# Chef Automate UI access
curl -k https://localhost

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
```