---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that download and install Chef Automate CLI, deploy Chef Automate and/or Chef Infra Server, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Configuration Management Server

**Configured Instances**:
- **Chef Automate Server**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that perform similar operations:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates an initial admin user with specified credentials
   - Creates an initial organization and associates the admin user
   - Generates and saves user and organization PEM files
   - Resources: sysctl (2), curl (1), file permissions (1), chef-automate CLI (1), chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value
   - Configures system parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only the Chef Infra Server product (without Automate)
   - Creates an initial admin user with specified credentials
   - Creates an initial organization and associates the admin user
   - Generates and saves user and organization PEM files
   - Resources: sysctl (2), curl (1), file permissions (1), chef-automate CLI (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Admin User Details

- **Variable(s)**: `username`, `longusername`, `useremail`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

### Organization Details

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial organization in Chef Infra Server

### PEM Files

- **Variable(s)**: `userfilename`, `orgfilename`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Generated files
- **Usage context**: Authentication keys for the admin user and organization validator

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/hostname
- ${username}.pem (admin user key file)
- ${orgname}-validator.pem (organization validator key file)
- /etc/chef-automate/config.toml (Chef Automate configuration)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /etc/hostname
cat /etc/hosts | grep $(hostname)
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status
curl -k https://localhost/api/_status

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health
curl -k https://localhost/api/v0/health

# Logs
sudo chef-automate system-logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# Resources
df -h /var/opt/chef-automate
df -h /var/opt/opscode
free -m
```