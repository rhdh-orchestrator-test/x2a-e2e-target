---
source-path: setup-automate
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using shell scripts. It configures a single instance with user and organization setup. The scripts handle system requirements, download and installation of Chef components, and initial configuration.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate and Infra Server**: Combined deployment of Chef Automate and Chef Infra Server
  - Location/Path: Default installation paths
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: User and organization creation with authentication keys

- **Chef Infra Server**: Standalone Chef Infra Server deployment
  - Location/Path: Default installation paths
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: User and organization creation with authentication keys

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value
   - Configures system requirements:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates initial admin user with specified credentials
   - Creates organization and associates admin user
   - Generates and saves authentication key files
   - Resources: sysctl (2), curl (1), chmod (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value
   - Configures system requirements:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server with acceptance of terms
   - Creates initial admin user with specified credentials
   - Creates organization and associates admin user
   - Generates and saves authentication key files
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

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial admin user in Chef Automate/Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be set to 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be set to 20000)
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are used in this module.

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

# User verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health check
curl -k https://localhost/api/_status

# Chef Automate API check (requires token)
# Get token first
TOKEN=$(sudo chef-automate admin-token)
curl -k -H "api-token: $TOKEN" https://localhost/api/v0/auth/version

# Chef Infra Server API check
curl -k --key jtonello.pem --cert jtonello.pem https://localhost/organizations/lab/nodes

# Logs
sudo journalctl -u chef-automate -f
sudo journalctl -u chef-server -f

# Resource usage
df -h
free -m
top -n 1
```