---
source-path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
---

# Migration Plan: Chef Server Deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Infra Server and Chef Automate on a VM. The scripts set up the hostname, system parameters, download and install Chef components, and create initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server and Chef Automate)

**Configured Instances**:

- **Chef Infra Server**: Core Chef server component
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization creation

- **Chef Automate**: Chef's observability and automation platform
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Infra Server

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes it executable
   - Resources: curl, gunzip, chmod

3. **Chef Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys Chef Infra Server using the chef-automate CLI
   - Uses --product infra-server flag
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

4. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys both Chef Automate and Chef Infra Server using the chef-automate CLI
   - Uses --product automate --product infra-server flags
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

5. **User and Organization Creation** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (e.g., 'jtonello')
     - Full name (e.g., 'John Tonello')
     - Email (e.g., 'jtonello@chef.lab')
     - Password (e.g., 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name (e.g., 'lab')
     - Full name (e.g., 'Chef Lab')
     - Associates the created user
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate requires PostgreSQL and Elasticsearch internally

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count
- /proc/sys/vm/dirty_expire_centisecs
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate CLI
which chef-automate
chef-automate version

# Chef Infra Server status
sudo chef-server-ctl status
curl -k https://localhost/organizations

# Chef Automate status (if deployed)
sudo chef-automate status
curl -k https://localhost/api/v0/auth/version

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
sudo netstat -tulpn | grep :443
sudo ss -tlnp | grep :443

# Service status
sudo systemctl status chef-server
sudo chef-server-ctl service-list

# Logs
sudo chef-server-ctl tail
sudo journalctl -u chef-server

# If Chef Automate is deployed
sudo systemctl status automate
sudo journalctl -u automate
```