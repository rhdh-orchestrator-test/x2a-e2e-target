---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures system settings, downloads the Chef Automate CLI, deploys the services, and creates initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - URL: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Saves as executable: chef-automate
   - Deploys Chef Automate and Chef Infra Server:
     - Command: chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
   - Creates initial Chef user:
     - Command: chef-server-ctl user-create jtonello "John Tonello" jtonello@chef.io userpassword
     - Saves user key to jtonello.pem
   - Creates initial Chef organization:
     - Command: chef-server-ctl org-create lab "Chef Lab" --association_user jtonello
     - Saves organization validator key to lab-validator.pem
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - URL: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Saves as executable: chef-automate
   - Deploys only Chef Infra Server:
     - Command: chef-automate deploy --product infra-server --accept-terms-and-mlsa=true
   - Creates initial Chef user:
     - Command: chef-server-ctl user-create jtonello "John Tonello" jtonello@chef.io userpassword
     - Saves user key to jtonello.pem
   - Creates initial Chef organization:
     - Command: chef-server-ctl org-create lab "Chef Lab" --association_user jtonello
     - Saves organization validator key to lab-validator.pem
   - Resources: system configuration (2), download (1), deployment (1), user creation (1), organization creation (1)

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
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ./chef-automate (executable file)
- ./jtonello.pem (user key file)
- ./lab-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (bash scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ./jtonello.pem
ls -la ./lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/api/v0/status

# Chef Server API access
curl -k https://localhost/organizations/lab

# Service logs
sudo ./chef-automate system-logs
journalctl -u chef-automate
```