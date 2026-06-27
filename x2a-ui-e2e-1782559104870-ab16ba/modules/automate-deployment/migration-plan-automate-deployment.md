---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures system settings, downloads the Chef Automate CLI, deploys the Chef products, and sets up initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate or standalone depending on script used

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Downloads the Chef Automate CLI from packages.chef.io
   - Extracts and makes the CLI executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flags

   **OR**

   **Chef Infra Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flag

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Creates an initial admin user with specified credentials
   - Creates an organization and associates the admin user with it
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-automate/config.toml` (Chef Automate configuration)
- `/etc/opscode/` (Chef Infra Server configuration directory)
- User PEM file (e.g., `jtonello.pem`)
- Organization validator PEM file (e.g., `lab-validator.pem`)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UIs)
- Network interfaces: All interfaces by default

**Templates rendered**:
- No templates are explicitly rendered in these scripts

## Pre-flight checks:
```bash
# System configuration checks
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Service status checks
sudo chef-automate status
sudo chef-server-ctl status

# Chef Automate API health check
curl -k https://localhost/api/v0/health

# Chef Infra Server API health check
curl -k https://localhost/organizations

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Log verification
sudo chef-automate system-logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# Disk space and resource usage
df -h
free -m
top -n 1
```