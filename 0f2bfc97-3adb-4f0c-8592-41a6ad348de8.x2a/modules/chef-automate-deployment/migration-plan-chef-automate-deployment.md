# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with customizable user and organization settings, system tuning, and proper certificate generation.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **chef-automate**: Chef Automate server with integrated Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Chef Automate UI, 8989 for Chef Infra Server)
  - Key Config: Custom hostname, user creation, organization creation

- **chef-infra-server**: Standalone Chef Infra Server (separate deployment script)
  - Location/Path: Installed on the local system
  - Port/Socket: Default port (8989)
  - Key Config: Custom hostname, user creation, organization creation

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of bash scripts that perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Deploys Chef Automate with integrated Chef Infra Server using the CLI tool
   - Creates a user in Chef Infra Server with specified credentials
   - Creates an organization in Chef Infra Server and associates the user
   - Generates and saves user and organization validator PEM files
   - Resources: sysctl (2), curl (1), file permission (1), chef-automate CLI (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Tunes kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool from packages.chef.io
   - Deploys only Chef Infra Server (without Automate) using the CLI tool
   - Creates a user in Chef Infra Server with specified credentials
   - Creates an organization in Chef Infra Server and associates the user
   - Generates and saves user and organization validator PEM files
   - Resources: sysctl (2), curl (1), file permission (1), chef-automate CLI (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined (Chef Automate manages its own services)

## Checks for the Migration

**Files to verify**:
- /etc/chef/[username].pem (e.g., jtonello.pem)
- /etc/chef/[orgname]-validator.pem (e.g., lab-validator.pem)
- /etc/systemd/system/chef-automate.service
- /var/log/chef-automate/

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI), 8989 (Chef Infra Server)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (uses Chef Automate's built-in templates)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Certificate verification
ls -la /etc/chef/jtonello.pem
ls -la /etc/chef/lab-validator.pem
openssl x509 -in /etc/chef/jtonello.pem -text -noout

# Service status
systemctl status chef-automate
journalctl -u chef-automate

# Network listening
netstat -tulpn | grep 443
netstat -tulpn | grep 8989
curl -k https://localhost/api/v0/health

# UI access
curl -k https://localhost/api/v0/version
curl -k https://localhost:443 | grep -i chef

# Chef Infra Server API access
knife user list -s https://localhost:8989 -u jtonello -k /etc/chef/jtonello.pem

# Logs
tail -f /var/log/chef-automate/automate-deploy.log
```