---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure Chef Automate and Chef Infra Server on a VM, create a user, and create an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The setup-automate module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Saves user and organization validator keys to files
   - Resources: System commands (hostnamectl, sysctl), curl, file operations, Chef Automate CLI

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the created user with it
   - Saves user and organization validator keys to files
   - Resources: System commands (hostnamectl, sysctl), curl, file operations, Chef Automate CLI

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used for creating the initial admin user in Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/hostname (for hostname configuration)
- User key file: [username].pem (default location: current directory)
- Organization validator key file: [orgname]-validator.pem (default location: current directory)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
cat /etc/hosts | grep $(hostname)
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status (if deploy-automate.sh was used)
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
ls -la ./*.pem
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Service health
curl -k https://localhost/api/v0/health

# Chef Automate UI access
curl -k -I https://localhost

# Chef Infra Server API access
curl -k -I https://localhost/organizations

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail

# Resource usage
top -n 1
free -m
df -h
```