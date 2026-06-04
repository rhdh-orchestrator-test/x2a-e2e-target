---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in one script, standalone in the other

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, email, and password
   - Creates an organization with the configured name
   - Generates and saves user and organization PEM files
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI execution, user creation, organization creation

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, email, and password
   - Creates an organization with the configured name
   - Generates and saves user and organization PEM files
   - Resources: hostname configuration, sysctl parameters, file download, Chef Automate CLI execution, user creation, organization creation

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly managed via systemd

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
which chef-automate
chef-automate version

# Chef Automate status (if deploy-automate.sh was used)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# PEM files
ls -la ~/${username}.pem  # Should exist and be readable
ls -la ~/${orgname}-validator.pem  # Should exist and be readable

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443
curl -k https://localhost/_status  # Chef Infra Server status endpoint

# Web UI access
curl -k -I https://localhost  # Should return HTTP 200 OK for Chef Automate UI

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs
```