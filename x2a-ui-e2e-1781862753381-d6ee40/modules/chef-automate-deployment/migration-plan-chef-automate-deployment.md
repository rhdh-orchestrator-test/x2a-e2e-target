---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server on a single VM. It configures system settings, downloads and installs Chef Automate CLI, deploys the products, and creates an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, chmod (2)

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy (1)

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
   - Creates organization and associates the admin user
   - Generates and saves user and organization PEM files
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

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
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/sysctl.conf or /etc/sysctl.d/* (for kernel parameter settings)
- Generated PEM files: [username].pem and [orgname]-validator.pem

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate and Chef Infra Server status
sudo chef-automate status
curl -k https://localhost/api/_status

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443
lsof -i :443

# Service health
curl -k https://localhost/api/v0/health
curl -k https://localhost/organizations/lab

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
sudo chef-server-ctl tail

# System resources
df -h
free -m
top -n 1
```