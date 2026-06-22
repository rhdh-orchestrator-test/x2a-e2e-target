---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: Deployed as a single instance with configurable hostname
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (HTTPS)
  - Key Config: Configured with user and organization details

- **Chef Infra Server (standalone)**: Deployed as a single instance with configurable hostname
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (HTTPS)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the created user with it
   - Saves user and organization validator keys to local files
   - Resources: sysctl (2), curl/gunzip, chef-automate CLI (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization and associates the created user with it
   - Saves user and organization validator keys to local files
   - Resources: sysctl (2), curl/gunzip, chef-automate CLI (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

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
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `chef-automate` executable in the current directory
- User PEM file (e.g., `jtonello.pem`) in the current directory
- Organization validator PEM file (e.g., `lab-validator.pem`) in the current directory

**Service endpoints to check**:
- Chef Automate UI: https://{hostname}
- Chef Infra Server API: https://{hostname}/organizations/{orgname}

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files existence
ls -la jtonello.pem
ls -la lab-validator.pem

# Test Chef Infra Server API access
knife ssl check -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem

# Check Chef Automate UI accessibility
curl -k -I https://automate.chef.lab

# Check services are running
sudo systemctl status chef-automate
sudo chef-server-ctl service-list

# Check logs
sudo chef-automate system-logs

# Network listening
sudo netstat -tulpn | grep -E '443|80'
sudo ss -tlnp | grep -E '443|80'

# Resource usage
sudo chef-automate status
df -h
free -m
```