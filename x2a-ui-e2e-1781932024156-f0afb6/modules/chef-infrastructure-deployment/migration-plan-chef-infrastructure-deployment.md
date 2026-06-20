---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple Chef infrastructure deployment module consisting of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set up a Chef server with a single user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: A single instance of Chef Automate with integrated Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Chef Automate UI, 8989 for Chef Infra Server)
  - Key Config: Creates a user and organization with associated PEM files

- **Chef Infra Server (standalone)**: A single instance of Chef Infra Server without Automate
  - Location/Path: Installed on the local system
  - Port/Socket: Default port (8989)
  - Key Config: Creates a user and organization with associated PEM files

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures kernel parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate with Chef Infra Server using the CLI tool
   - Creates a user with the specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM files for the user and organization
   - Resources: sysctl (2), curl (1), file permission (1), chef-automate CLI (1), chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the configured value
   - Configures kernel parameters for optimal Chef Infra Server performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) using the CLI tool
   - Creates a user with the specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM files for the user and organization
   - Resources: sysctl (2), curl (1), file permission (1), chef-automate CLI (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly managed (Chef Automate and Chef Infra Server are installed but not managed as services in these scripts)

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
- ~/${username}.pem (user PEM file)
- ~/${orgname}-validator.pem (organization validator PEM file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI), 8989 (Chef Infra Server)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (no templates are used in these scripts)

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

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# PEM files existence and permissions
ls -la ~/${username}.pem
ls -la ~/${orgname}-validator.pem

# Network listening
netstat -tulpn | grep 443  # Chef Automate UI
netstat -tulpn | grep 8989  # Chef Infra Server
ss -tlnp | grep 443
ss -tlnp | grep 8989

# Web UI accessibility
curl -k https://localhost/api/v0/health

# Chef Server API accessibility
knife user list -s https://localhost:8989 -u $username -k ~/${username}.pem

# Log files
sudo tail -f /var/log/chef-automate/automate-deployment.log
```