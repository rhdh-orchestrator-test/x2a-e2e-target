---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef infrastructure deployment module consisting of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Configuration Management Server

**Configured Instances**:
- **Chef Automate with Infra Server**: Deploys both Chef Automate and Chef Infra Server on a single VM
  - Location/Path: Local system
  - Port/Socket: Default Chef Automate ports (443)
  - Key Config: User creation, organization creation, system parameters

- **Chef Infra Server**: Deploys only Chef Infra Server without Automate
  - Location/Path: Local system
  - Port/Socket: Default Chef Server ports (443)
  - Key Config: User creation, organization creation, system parameters

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The setup-automate module performs operations in this order:

1. **deploy-automate.sh**:
   - Sets hostname to the configured value using hostnamectl
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from packages.chef.io
     - Extracts and makes executable
   - Deploys Chef Automate and Chef Infra Server:
     - Uses chef-automate deploy command
     - Accepts terms and MLSA
     - Installs both products (automate and infra-server)
   - Creates initial user:
     - Uses chef-server-ctl user-create
     - Creates user with specified username, name, email, password
     - Saves user key to [username].pem file
   - Creates initial organization:
     - Uses chef-server-ctl org-create
     - Creates organization with specified short and long names
     - Associates the created user with the organization
     - Saves organization validator key to [orgname]-validator.pem file
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets hostname to the configured value using hostnamectl
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - Downloads from packages.chef.io
     - Extracts and makes executable
   - Deploys Chef Infra Server only:
     - Uses chef-automate deploy command
     - Accepts terms and MLSA
     - Installs only infra-server product
   - Creates initial user:
     - Uses chef-server-ctl user-create
     - Creates user with specified username, name, email, password
     - Saves user key to [username].pem file
   - Creates initial organization:
     - Uses chef-server-ctl org-create
     - Creates organization with specified short and long names
     - Associates the created user with the organization
     - Saves organization validator key to [orgname]-validator.pem file
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate, chef-server-ctl (2)

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

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef administrator user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- [username].pem (user key file)
- [orgname]-validator.pem (organization validator key file)
- Chef Automate configuration files (created by chef-automate deploy)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (for deploy-automate.sh)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep [username]

# Organization verification
sudo chef-server-ctl org-list | grep [orgname]

# Key files
ls -la [username].pem
ls -la [orgname]-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://localhost/_status

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
```