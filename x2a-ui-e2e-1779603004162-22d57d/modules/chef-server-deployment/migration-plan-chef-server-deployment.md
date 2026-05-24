---
source-path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
---

# Migration Plan: chef-server-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Infra Server and Chef Automate on a Linux system. The scripts set system parameters, download Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server and Chef Automate)

**Configured Instances**:

- **Chef Infra Server**: Chef server installation without Automate
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization creation

- **Chef Automate with Infra Server**: Combined Chef Automate and Chef Infra Server installation
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization creation, system parameter tuning

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Product Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product infra-server flag

4. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys both Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product automate --product infra-server flags

5. **User and Organization Creation** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Creates a user with the configured username, name, email, and password
   - Creates an organization with the configured organization name
   - Associates the created user with the organization
   - Saves user and organization validator keys to files
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

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
- **Source file(s)**: `setup-automate/deploy-chef-server.sh`, `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef server user

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count
- /proc/sys/vm/dirty_expire_centisecs
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should exist and be executable

# Chef Infra Server status
sudo chef-server-ctl status
curl -k https://localhost  # Should return Chef Infra Server page

# Chef Automate status (if deployed)
sudo chef-automate status
curl -k https://localhost/api/v0/auth/version  # Should return Automate API version

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user
sudo chef-server-ctl org-list  # Should include the created organization

# Key files
ls -la ./${username}.pem  # Should exist
ls -la ./${orgname}-validator.pem  # Should exist

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Logs
sudo chef-server-ctl tail
sudo chef-automate system-logs

# Service status
sudo chef-server-ctl status
sudo chef-automate status
```