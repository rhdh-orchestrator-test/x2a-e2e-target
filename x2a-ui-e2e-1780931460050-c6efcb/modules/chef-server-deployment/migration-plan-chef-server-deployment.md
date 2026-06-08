---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Infra Server and Chef Automate on a VM. The scripts set system parameters, download and install Chef components, and configure a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server and Chef Automate)

**Configured Instances**:

- **Chef Infra Server**: A standalone Chef server installation
  - Location/Path: Installed on the local system
  - Port/Socket: Default Chef Server ports (443, 80)
  - Key Config: User and organization creation

- **Chef Automate**: Chef's observability and automation platform
  - Location/Path: Installed on the local system alongside Chef Infra Server
  - Port/Socket: Default Chef Automate ports (443)
  - Key Config: Integrated with Chef Infra Server

## File Structure

```
No Chef recipe files found
No provider files found
No template files found
No attribute files found
```

## Module Explanation

The module consists of two bash scripts that deploy Chef Infra Server and Chef Automate:

1. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Infra Server using the Chef Automate CLI
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for the user and organization validator

2. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys both Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for the user and organization validator

Both scripts use the same set of configurable variables:
- hostname: The hostname to set for the system
- username: The Chef user's username
- longusername: The Chef user's full name
- useremail: The Chef user's email address
- userpassword: The Chef user's password
- orgname: The Chef organization's short name
- longorgname: The Chef organization's full name

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-chef-server.sh, setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/opscode/
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS), 80 (HTTP)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered by these scripts.

## Pre-flight checks:
```bash
# System hostname check
hostname
hostnamectl

# System parameters check
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI check
ls -la chef-automate
./chef-automate version

# Chef Infra Server service status
sudo chef-server-ctl status
systemctl status chef-server

# Chef Automate service status (if deployed)
sudo chef-automate status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'
lsof -i :443

# Chef Server API check
curl -k https://localhost/_status
curl -k https://automate.chef.lab/_status

# Chef Automate API check (if deployed)
curl -k https://localhost/api/v0/auth/version
curl -k https://automate.chef.lab/api/v0/auth/version

# Logs
sudo chef-server-ctl tail
sudo journalctl -u chef-server
sudo chef-automate system-logs

# Disk space
df -h /var/opt/chef-server
df -h /var/opt/chef-automate
```