---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef deployment module consisting of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy the products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Chef Infrastructure Management Platform

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization name

- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization name

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The setup-automate module performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms and MLSA
   - Creates an initial admin user with the configured username, name, email, and password
   - Creates an organization and associates the admin user with it
   - Generates PEM key files for the user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal Chef Server performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms and MLSA
   - Creates an initial admin user with the configured username, name, email, and password
   - Creates an organization and associates the admin user with it
   - Generates PEM key files for the user and organization validator
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate deploy, chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, bash
**Service dependencies**: None explicitly defined (Chef Automate handles its own dependencies)

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (should contain the configured hostname)
- /etc/hostname (should be set to the configured hostname)
- User PEM file (e.g., jtonello.pem in the current directory)
- Organization validator PEM file (e.g., lab-validator.pem in the current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment scripts don't use templates)

## Pre-flight checks:
```bash
# System hostname check
hostname
cat /etc/hostname
cat /etc/hosts | grep $(hostname)

# System parameters check
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Check for PEM files
ls -la *.pem
file jtonello.pem
file lab-validator.pem

# Check Chef Automate services
sudo systemctl status chef-automate
curl -k https://localhost/api/v0/health

# Check Chef Infra Server services
sudo chef-server-ctl service-list
sudo chef-server-ctl status

# Verify user and organization
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail

# API check (requires the PEM file)
knife user list -s https://localhost/organizations/lab -u jtonello --key jtonello.pem

# Web UI access
curl -k -I https://localhost/
```