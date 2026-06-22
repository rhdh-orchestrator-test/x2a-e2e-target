---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: Deployed via deploy-automate.sh
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (Chef Automate UI), 9090 (Chef Infra Server API)
  - Key Config: Sets hostname, system parameters, and creates initial user/organization

- **Chef Infra Server (standalone)**: Deployed via deploy-chef-server.sh
  - Location/Path: Installed on the local system
  - Port/Socket: 443 (Chef Infra Server API)
  - Key Config: Sets hostname, system parameters, and creates initial user/organization

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization with the configured name and associates the user
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

2. **deploy-chef-server.sh**:
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, name, email, and password
   - Creates an organization with the configured name and associates the user
   - Resources: hostname configuration (1), sysctl (2), download (1), deploy (1), user creation (1), organization creation (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate and Chef Infra Server services are installed

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
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ~/chef-automate (the downloaded CLI binary)
- ~/$userfilename (the user PEM file, e.g., jtonello.pem)
- ~/$orgfilename (the organization validator PEM file, e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI), 9090 (Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (no templates used in this cookbook)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ~/chef-automate
file ~/chef-automate

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
ls -la ~/$userfilename  # e.g., ~/jtonello.pem
ls -la ~/$orgfilename   # e.g., ~/lab-validator.pem

# Test API access
curl -k https://localhost/api/v0/auth/version --header "api-token: $(sudo chef-automate admin-token)"

# Test Chef Infra Server API
knife user list -s https://localhost/organizations/$orgname -u $username -k ~/$userfilename

# Network listening
netstat -tulpn | grep -E '443|9090'
ss -tlnp | grep -E '443|9090'

# Service status
systemctl status chef-automate
journalctl -u chef-automate -n 50

# Logs
sudo chef-automate logs
tail -f /var/log/chef-server/erchef/erchef.log
```