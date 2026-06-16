---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization settings

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Resources: curl command, file permission change

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate CLI command

4. **Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate CLI command

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates initial admin user with specified credentials
   - Saves user key to a PEM file
   - Command: `chef-server-ctl user-create $username $longusername $useremail "${userpassword}" --filename $userfilename`
   - Resources: chef-server-ctl command

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates initial organization
   - Associates the admin user with the organization
   - Saves organization validator key to a PEM file
   - Command: `chef-server-ctl org-create $orgname "${longorgname}" --association_user $username --filename $orgfilename`
   - Resources: chef-server-ctl command

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

### Chef Admin User Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the admin user

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on disk
- **Usage context**: Authentication key for the organization validator

### Chef Automate Credentials

- **Variable(s)**: Not explicitly defined in scripts, but generated during deployment
- **Source file(s)**: Generated during `chef-automate deploy` command
- **Current storage**: Generated files on disk
- **Usage context**: Authentication for Chef Automate web UI and API

## Checks for the Migration

**Files to verify**:
- /etc/chef/
- /etc/chef-server/
- /etc/chef-automate/
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) or as configured during deployment

**Templates rendered**:
None (deployment uses Chef Automate CLI which handles configuration internally)

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

# Verify services are running
systemctl status chef-automate
sudo chef-server-ctl service-list

# Check Chef Automate API
curl -k https://localhost/api/v0/auth/version

# Check Chef Infra Server API
curl -k https://localhost/organizations

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Check PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Verify connectivity with knife
knife ssl check -c /path/to/knife.rb

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Logs
sudo journalctl -u chef-automate
sudo chef-server-ctl tail

# Memory usage
free -m
ps aux | grep chef | sort -rn -k 4 | head -10

# Disk usage
df -h /var/opt/chef-automate
df -h /var/opt/chef-server
```