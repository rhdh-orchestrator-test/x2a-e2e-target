---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-setup

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up the hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: A single instance of Chef Automate with integrated Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user creation, organization creation

- **Chef Infra Server (standalone)**: A single instance of Chef Infra Server without Automate
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user creation, organization creation

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform similar operations with slight differences:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from the official Chef repository
   - Deploys Chef Automate with Chef Infra Server using the CLI
   - Creates an initial admin user with specified credentials
   - Creates an organization and associates the admin user with it
   - Generates and saves user and organization PEM files
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate CLI, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from the official Chef repository
   - Deploys only Chef Infra Server (without Automate) using the CLI
   - Creates an initial admin user with specified credentials
   - Creates an organization and associates the admin user with it
   - Generates and saves user and organization PEM files
   - Resources: hostnamectl, sysctl (2), curl, chmod, chef-automate CLI, chef-server-ctl (2)

The key difference between the scripts is in the deployment command:
- deploy-automate.sh: `sudo ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
- deploy-chef-server.sh: `sudo ./chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`

Both scripts use the same configurable variables:
- hostname: The hostname to set for the server
- username: Short username for the admin user
- longusername: Full name for the admin user
- useremail: Email address for the admin user
- userpassword: Password for the admin user
- orgname: Short name for the organization
- longorgname: Full name for the organization

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, hostnamectl (systemd)
**Service dependencies**: None explicitly defined, but the Chef Automate and Chef Infra Server services are installed and started

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: This credential is used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (bash scripts don't use templates)

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

# Chef Automate status (if deployed with Automate)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la ./jtonello.pem
ls -la ./lab-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://$(hostname)

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
```