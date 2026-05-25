---
source-path: setup-automate
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

No Chef recipes, providers, templates, or attribute files were found in this module. The module consists solely of two bash scripts that handle the deployment process.

## Module Explanation

The module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value using hostnamectl
   - Configures system parameters with sysctl:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from packages.chef.io
     - Makes the binary executable
   - Deploys Chef Automate and Chef Infra Server:
     - Uses ./chef-automate deploy command
     - Includes both automate and infra-server products
     - Accepts terms and MLSA
   - Creates initial Chef user:
     - Uses chef-server-ctl user-create command
     - Creates user with specified username, name, email, and password
     - Saves user key to a .pem file
   - Creates initial Chef organization:
     - Uses chef-server-ctl org-create command
     - Creates organization with specified short and long names
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostnamectl (1), sysctl (2), curl (1), chmod (1), chef-automate (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value using hostnamectl
   - Configures system parameters with sysctl:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from packages.chef.io
     - Makes the binary executable
   - Deploys Chef Infra Server only (without Automate):
     - Uses ./chef-automate deploy command
     - Includes only infra-server product
     - Accepts terms and MLSA
   - Creates initial Chef user:
     - Uses chef-server-ctl user-create command
     - Creates user with specified username, name, email, and password
     - Saves user key to a .pem file
   - Creates initial Chef organization:
     - Uses chef-server-ctl org-create command
     - Creates organization with specified short and long names
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: hostnamectl (1), sysctl (2), curl (1), chmod (1), chef-automate (1), chef-server-ctl (2)

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
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user with chef-server-ctl user-create command

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no templates in this module)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la chef-automate  # Should exist and be executable
./chef-automate version  # Should show version information

# Chef Automate status (if deployed with automate)
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/health  # Should return health status

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Key files
ls -la ${username}.pem  # Should exist
ls -la ${orgname}-validator.pem  # Should exist

# Network listening
netstat -tulpn | grep 443  # Should show services listening on port 443
ss -tlnp | grep 443  # Alternative to netstat

# Service logs
sudo chef-automate logs  # Check Chef Automate logs
sudo journalctl -u chef-server  # Check Chef Server logs

# Web UI access
curl -k https://localhost  # Should return HTTP 200 or redirect
```