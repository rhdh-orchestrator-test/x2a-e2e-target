---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization settings

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization settings

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI commands

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates a user with specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI commands

## Dependencies

**External cookbook dependencies**: None detected
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- /proc/sys/vm/max_map_count (modified by sysctl)
- /proc/sys/vm/dirty_expire_centisecs (modified by sysctl)
- chef-automate executable in the deployment directory
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are explicitly rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list  # Should include the created user (e.g., jtonello)

# Verify organization creation
sudo chef-server-ctl org-list  # Should include the created organization (e.g., lab)

# Check PEM files
ls -la jtonello.pem  # Or whatever username was configured
ls -la lab-validator.pem  # Or whatever orgname was configured

# Verify Chef Automate UI is accessible
curl -k https://localhost  # Should return HTTP 200 or redirect to login page

# Check services
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-automate logs
journalctl -u chef-automate
```