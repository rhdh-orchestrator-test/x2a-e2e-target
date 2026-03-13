# Migration Plan: chef-infrastructure-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts install and configure Chef server components with user and organization creation. No actual Chef cookbook is present - these are shell scripts that deploy Chef infrastructure.

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

The module performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for Chef Automate:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with a single command
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates user and organization PEM files
   - Resources: hostname configuration, sysctl settings, file download, Chef Automate CLI commands

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for Chef Infra Server:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate)
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates user and organization PEM files
   - Resources: hostname configuration, sysctl settings, file download, Chef Automate CLI commands

Both scripts use the same set of configurable variables:
- hostname: The hostname for the Chef server (default: 'automate.chef.lab')
- username: Chef admin username (default: 'jtonello')
- longusername: Full name for the Chef admin user (default: 'John Tonello')
- useremail: Email for the Chef admin user (default: 'jtonello@chef.lab')
- userpassword: Password for the Chef admin user (default: 'password')
- orgname: Short name for the Chef organization (default: 'lab')
- longorgname: Full name for the Chef organization (default: 'Chef Lab')

## Dependencies

**External cookbook dependencies**: None (these are shell scripts, not Chef cookbooks)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate and Chef Infra Server have their own dependencies

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)
- Chef Automate configuration files (in default locations)
- Chef Infra Server configuration files (in default locations)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (these are shell scripts, not Chef cookbooks)

## Pre-flight checks:
```bash
# Hostname verification
hostname
cat /etc/hostname

# Kernel parameter verification
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI verification
./chef-automate version

# Chef Automate status (if deployed with deploy-automate.sh)
sudo ./chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM file verification
ls -la ~/${username}.pem
ls -la ~/${orgname}-validator.pem

# Service status
systemctl status chef-automate
systemctl status chef-server

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Web UI accessibility
curl -k https://localhost/api/v0/status

# Chef server API accessibility
knife user list -s https://localhost/organizations/${orgname} -k ~/${username}.pem -u ${username}

# Log verification
journalctl -u chef-automate
journalctl -u chef-server
```