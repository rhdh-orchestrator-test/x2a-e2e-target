---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a VM using a bash script. It configures the hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system alongside Chef Automate
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The bash script performs operations in this order:

1. **Set hostname** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Resources: hostnamectl command (1)

2. **Configure system parameters** (`setup-automate/deploy-automate.sh`):
   - Sets vm.max_map_count=262144 for Elasticsearch
   - Sets vm.dirty_expire_centisecs=20000 for disk I/O optimization
   - Resources: sysctl command (2)

3. **Download Chef Automate CLI** (`setup-automate/deploy-automate.sh`):
   - Downloads the latest Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands (3)

4. **Deploy Chef Automate and Chef Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs the Chef Automate deployment command with both products
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command (1)

5. **Create initial user** (`setup-automate/deploy-automate.sh`):
   - Creates a user in Chef Infra Server with the configured details
   - Saves the user's private key to a .pem file
   - Resources: chef-server-ctl user-create command (1)

6. **Create initial organization** (`setup-automate/deploy-automate.sh`):
   - Creates an organization in Chef Infra Server
   - Associates the previously created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl org-create command (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires sufficient system resources for Chef Automate and Chef Infra Server

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef Infra Server user

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `chef-automate` executable in the current directory
- User PEM file (e.g., `jtonello.pem`) in the current directory
- Organization validator PEM file (e.g., `lab-validator.pem`) in the current directory

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for both Chef Automate and Chef Infra Server)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (bash script doesn't use templates)

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

# Chef Automate status
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://localhost/_status

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
journalctl -u chef-automate -f

# Logs
sudo ./chef-automate logs
tail -f /var/log/chef-server/nginx/access.log
tail -f /var/log/chef-server/nginx/error.log

# API connectivity test (using the created user's PEM file)
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem
```