---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It configures a single instance with user and organization setup. The script sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Single instance deployment
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Single instance deployment
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

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, file permissions, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified details:
     - Username, full name, email, and password
     - Generates user key file (e.g., jtonello.pem)
   - Creates organization with specified details:
     - Organization short name and full name
     - Associates admin user with organization
     - Generates organization validator key file (e.g., lab-validator.pem)
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in deploy-automate.sh

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Initial admin user password for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef/jtonello.pem (or configured username.pem)
- /etc/chef/lab-validator.pem (or configured orgname-validator.pem)
- Chef Automate configuration files (default locations)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (uses default templates from Chef Automate installer)

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

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello  # or configured username
sudo chef-server-ctl org-list | grep lab  # or configured orgname

# Key files verification
ls -la jtonello.pem  # or configured username.pem
ls -la lab-validator.pem  # or configured orgname-validator.pem

# Web UI accessibility
curl -k https://localhost/api/v0/auth/version
curl -k https://automate.chef.lab/api/v0/auth/version  # or configured hostname

# Chef Infra Server API accessibility
knife ssl check -s https://automate.chef.lab/organizations/lab  # or configured hostname/orgname

# Service status
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Logs
sudo chef-automate system-logs
sudo chef-server-ctl tail

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Resource usage
df -h  # Check disk space
free -m  # Check memory usage
top -n 1  # Check CPU usage
```