---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: sysctl (2), curl (1), chmod (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: sysctl (2), curl (1), chmod (1), chef-automate deploy (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user for authentication to Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`
- `/etc/chef/`
- User PEM file: `[username].pem`
- Organization validator PEM file: `[orgname]-validator.pem`

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Hostname configuration
hostname
hostnamectl

# Service status
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/_status

# Chef Infra Server API access
curl -k https://localhost/organizations
curl -k https://localhost/_status

# User and organization verification
sudo chef-server-ctl user-list | grep [username]
sudo chef-server-ctl org-list | grep [orgname]

# PEM file verification
ls -la [username].pem
ls -la [orgname]-validator.pem

# Test user authentication
knife user list -s https://localhost -u [username] -k [username].pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs
sudo chef-server-ctl tail

# Resource usage
top -n 1
free -m
df -h
```