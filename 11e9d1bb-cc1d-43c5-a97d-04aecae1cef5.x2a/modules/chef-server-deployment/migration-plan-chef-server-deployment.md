# Migration Plan: chef-server-deployment

**TLDR**: This module consists of two bash scripts for deploying Chef Infra Server and Chef Automate on a single VM. The scripts set up the hostname, system parameters, download and install Chef components, and create initial user and organization configurations.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server and Chef Automate)

**Configured Instances**:

- **Chef Infra Server**: Core Chef server component
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization creation

- **Chef Automate**: Chef's observability and automation platform
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Infra Server

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Infra Server using the CLI tool with MLSA acceptance
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate CLI, chef-server-ctl (2)

2. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys both Chef Automate and Chef Infra Server using the CLI tool with MLSA acceptance
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate CLI, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None (scripts are standalone)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined (Chef Automate manages its own dependencies)

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/sysctl.conf or /etc/sysctl.d/* (for sysctl parameters)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)
- Chef Automate configuration files (created during deployment)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la chef-automate
./chef-automate version

# Service status
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Chef Server API access
curl -k https://localhost/organizations
curl -k https://localhost/_status

# Chef Server user verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Chef Server functionality test
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem --no-editor

# Chef Automate UI access
curl -k https://localhost
curl -k https://localhost/api/v0/auth/version

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Resource usage
df -h
free -m
top -n 1
```