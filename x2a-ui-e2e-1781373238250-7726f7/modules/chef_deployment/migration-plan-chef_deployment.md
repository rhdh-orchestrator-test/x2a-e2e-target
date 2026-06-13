---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A complete DevOps platform that includes Chef Infra Server, Chef Habitat, and Chef InSpec
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Configuration management server (standalone option)
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The setup-automate module performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from the official Chef repository
   - Deploys Chef Automate and Chef Infra Server with the --accept-terms-and-mlsa flag
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM key files for the user and organization validator
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from the official Chef repository
   - Deploys only Chef Infra Server (without Automate) with the --accept-terms-and-mlsa flag
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Generates PEM key files for the user and organization validator
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

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

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameter verification
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI verification
ls -la ./chef-automate
./chef-automate version

# Service status (for Chef Automate deployment)
sudo chef-automate status

# Service status (for Chef Infra Server)
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key file verification
ls -la ./jtonello.pem
ls -la ./lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/_status

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Process verification
ps aux | grep chef-server
ps aux | grep automate

# Log verification
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# System resources
free -m
df -h
```