---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a single instance of Chef Automate with integrated Chef Infra Server, configures system parameters, creates an initial admin user, and establishes an organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Single instance deployment with integrated Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with integrated Chef Infra Server
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials:
     - Username: Configured value (default: 'jtonello')
     - Full name: Configured value (default: 'John Tonello')
     - Email: Configured value (default: 'jtonello@chef.lab')
     - Password: Configured value (default: 'password')
     - Generates user key file: [username].pem
   - Creates organization with specified details:
     - Organization short name: Configured value (default: 'lab')
     - Organization full name: Configured value (default: 'Chef Lab')
     - Associates admin user with organization
     - Generates organization validator key: [orgname]-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None (this script installs the services)

## Credentials

**Detection Summary**: 4 credentials detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Initial admin user password for Chef Automate and Chef Infra Server

### Chef Admin User Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for Chef Infra Server API access

### Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for bootstrapping new nodes to the Chef organization

### Chef Automate Credentials

- **Variable(s)**: Not explicitly shown in script, but generated during deployment
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: Generated during deployment
- **Usage context**: Authentication for Chef Automate web UI and API access

## Checks for the Migration

**Files to verify**:
- /etc/chef/[username].pem
- /etc/chef/[orgname]-validator.pem
- /etc/systemd/system/chef-automate.service
- /var/log/chef-automate/

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (deployment script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate service status
sudo chef-automate status
systemctl status chef-automate

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# API connectivity test
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k /etc/chef/jtonello.pem

# Web UI access
curl -k https://automate.chef.lab/
curl -k https://automate.chef.lab/api/v0/health

# SSL certificate verification
openssl s_client -connect automate.chef.lab:443 -showcerts

# Log verification
sudo tail -f /var/log/chef-automate/automate-deployment.log

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Resource usage
sudo chef-automate status
df -h
free -m
```