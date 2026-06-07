---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Deployed alongside Chef Automate or standalone
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets the hostname to the configured value using `hostnamectl`
   - Configures kernel parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Resources: curl command, chmod command (2)

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command (1)

4. **Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command (1)

5. **User and Organization Setup** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user with the configured details using chef-server-ctl
   - Creates an organization with the configured details using chef-server-ctl
   - Associates the created user with the organization
   - Generates PEM files for user and organization authentication
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but requires systemd for hostnamectl

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user authentication key)
- ~/${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered directly by these scripts.

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

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Service status
systemctl status chef-automate
```