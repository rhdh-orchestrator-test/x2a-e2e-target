---
source-path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and/or Chef Infra Server using shell scripts. It configures a single instance of each service with basic user and organization setup. The scripts handle hostname configuration, system tuning, downloading the Chef Automate CLI, deploying the services, and creating initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**:
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server product (without Automate)
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` (should contain the configured hostname)
- `~/${username}.pem` (admin user key file)
- `~/${orgname}-validator.pem` (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# Kernel parameter verification
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status (if deployed)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Key file verification
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Service health check
curl -k https://localhost/_status
curl -k https://localhost/organizations/lab

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Process verification
ps aux | grep chef-server
ps aux | grep automate

# Log verification
sudo journalctl -u chef-server
sudo journalctl -u automate

# System resources
df -h
free -m
top -n 1 | head -15
```