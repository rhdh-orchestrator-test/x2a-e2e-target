---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization creation. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: A single Chef Automate instance
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A single Chef Infra Server instance
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate, user and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: automate.chef.lab)
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef Automate with Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate CLI

3. **Chef Infra Server Installation** (`setup-automate/deploy-chef-server.sh`):
   - Similar to Chef Automate installation but only deploys the Infra Server product
   - Resources: curl, file permissions, chef-automate CLI

4. **User and Organization Setup** (both scripts):
   - Creates a Chef user with:
     - Username (default: jtonello)
     - Full name (default: John Tonello)
     - Email (default: jtonello@chef.lab)
     - Password (default: password)
     - Saves user key to [username].pem file
   - Creates a Chef organization with:
     - Short name (default: lab)
     - Full name (default: Chef Lab)
     - Associates the created user with the organization
     - Saves organization validator key to [orgname]-validator.pem
   - Resources: chef-server-ctl commands (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires standard Linux system services

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
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count
- /proc/sys/vm/dirty_expire_centisecs
- [username].pem (user key file)
- [orgname]-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment scripts don't use templates)

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
ls -la jtonello.pem
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem
sudo chef-server-ctl org-show lab

# Service status
systemctl status chef-automate
ss -tulpn | grep 443

# Web UI accessibility
curl -k https://localhost/api/v0/auth/version
curl -k https://localhost/organizations

# Log verification
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Backup verification (if applicable)
sudo chef-automate backup status
```