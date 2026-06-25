---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations. There are no actual Chef cookbooks involved, just bash scripts that install Chef products.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. There are no actual Chef cookbooks or recipes involved.

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates initial user with specified username, name, email, and password
   - Creates initial organization with specified name and associates it with the user
   - Resources: system configuration, Chef Automate CLI, user creation, organization creation

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates initial user with specified username, name, email, and password
   - Creates initial organization with specified name and associates it with the user
   - Resources: system configuration, Chef Automate CLI, user creation, organization creation

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

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: This credential is used as the password for the initial Chef admin user created during deployment

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef/
- Generated PEM files: `$username.pem` and `$orgname-validator.pem` in the current directory

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Hostname configuration
hostname
hostnamectl

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Check Chef Automate UI
curl -k https://localhost/api/v0/auth/version

# Check Chef Infra Server API
curl -k https://localhost/organizations

# Check user and organization
sudo chef-server-ctl user-list
sudo chef-server-ctl org-list

# Verify PEM files
ls -la $username.pem
ls -la $orgname-validator.pem

# Test user authentication
knife user list -s https://localhost/organizations/$orgname -u $username -k $username.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service logs
sudo journalctl -u chef-automate
sudo journalctl -u chef-server

# Check disk space
df -h /var/opt/chef-automate
df -h /var/opt/chef-server
```