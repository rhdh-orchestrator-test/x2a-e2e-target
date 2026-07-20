---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef Automate and Chef Infra Server deployment module consisting of two bash scripts that install and configure Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with --accept-terms-and-mlsa=true
   - Creates a user with specified credentials:
     - Username, full name, email, and password
     - Saves user key to [username].pem file
   - Creates an organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to [orgname]-validator.pem file
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures system parameters:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) with --accept-terms-and-mlsa=true
   - Creates a user with specified credentials:
     - Username, full name, email, and password
     - Saves user key to [username].pem file
   - Creates an organization:
     - Organization short name and full name
     - Associates the created user with the organization
     - Saves organization validator key to [orgname]-validator.pem file
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- [username].pem (user key file)
- [orgname]-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep [username]
ls -la [username].pem
sudo chef-server-ctl user-show [username]

# Organization verification
sudo chef-server-ctl org-list | grep [orgname]
ls -la [orgname]-validator.pem
sudo chef-server-ctl org-show [orgname]

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/health

# Log verification
sudo journalctl -u chef-automate
sudo journalctl -u chef-server

# Certificate verification
openssl x509 -in /var/opt/chef-automate/cert/HOSTNAME.crt -text -noout
```