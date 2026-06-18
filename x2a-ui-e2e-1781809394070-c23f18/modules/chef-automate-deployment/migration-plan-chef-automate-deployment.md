---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures system settings, downloads and installs Chef Automate CLI, deploys the Chef products, and creates initial user and organization.

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

The module consists of bash scripts that perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flags

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates organization with:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates admin user with organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The alternative script (`setup-automate/deploy-chef-server.sh`) performs the same operations but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script variable
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ${username}.pem (user key file, default: jtonello.pem)
- ${orgname}-validator.pem (organization validator key, default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (direct deployment without templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Verify key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Check Chef Automate UI accessibility
curl -k https://localhost/api/v0/auth/version

# Check Chef Infra Server API accessibility
curl -k https://localhost/organizations/lab

# Verify services are running
sudo systemctl status chef-automate
ps aux | grep chef

# Check logs
sudo journalctl -u chef-automate -f
sudo chef-automate logs

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Resource usage
df -h
free -m
top -n 1 | head -20
```