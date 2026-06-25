---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two shell scripts that deploy Chef Automate and Chef Infra Server. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization settings

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization settings

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: sysctl (2), curl (1), file permission (1), chef-automate CLI (1), chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: sysctl (2), curl (1), file permission (1), chef-automate CLI (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate may have its own dependencies

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
- **Usage context**: Used for creating the initial Chef user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are used in this cookbook.

## Pre-flight checks:

```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la jtonello.pem

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/_status

# Log verification
sudo journalctl -u chef-automate
sudo journalctl -u chef-server

# Service health
sudo systemctl status chef-automate
sudo systemctl status chef-server
```