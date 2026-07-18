---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This cookbook consists of two shell scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, configure system parameters, download Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: A single instance of Chef Automate with integrated Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for Chef Automate UI)
  - Key Config: User and organization creation

- **Chef Infra Server (standalone)**: A single instance of Chef Infra Server without Automate
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for Chef Server UI)
  - Key Config: User and organization creation

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate with Chef Infra Server
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate deployment, user creation, organization creation

2. **deploy-chef-server.sh**:
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate)
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Infra Server deployment, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip (part of gzip package)
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (e.g., jtonello.pem in the directory where the script was run)
- Organization validator PEM file (e.g., lab-validator.pem in the directory where the script was run)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Chef Server UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la chef-automate
./chef-automate version

# Chef Automate status (if deployed with Automate)
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Chef Server API accessibility
knife user list -s https://localhost/organizations/lab -k jtonello.pem -u jtonello

# Log verification
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50
```