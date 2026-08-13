---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of Bash scripts for deploying Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

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
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Resources: curl, chmod

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flags

4. **Standalone Chef Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server (without Automate)
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Setup** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates initial admin user with specified credentials
   - Creates organization and associates the admin user
   - Generates and saves user and organization validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, hostnamectl (systemd)
**Service dependencies**: None explicitly defined, but requires systemd for hostname setting

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

### Chef Admin User PEM File

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on filesystem
- **Usage context**: Authentication key for the admin user

### Chef Organization Validator PEM File

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated file on filesystem
- **Usage context**: Authentication key for the organization validator

### Chef Automate Credentials

- **Variable(s)**: Not explicitly defined in scripts, but generated during deployment
- **Source file(s)**: Generated during `chef-automate deploy` command
- **Current storage**: Generated during installation
- **Usage context**: Authentication for Chef Automate web UI

## Checks for the Migration

**Files to verify**:
- /etc/chef/client.rb (if created)
- /etc/chef/validation.pem (if created)
- /etc/hostname (modified by the script)
- ${username}.pem (admin user key file)
- ${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the configured username
ls -la ${username}.pem  # Should exist and have proper permissions

# Organization verification
sudo chef-server-ctl org-list  # Should include the configured orgname
ls -la ${orgname}-validator.pem  # Should exist and have proper permissions

# Web UI access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/organizations/${orgname}  # Should verify Chef Infra Server organization

# Network listening
netstat -tulpn | grep 443  # Should show services listening on port 443
ss -tlnp | grep 443  # Alternative check for services listening on port 443

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs

# API access test (requires the PEM file)
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ${username}.pem  # Should list users without errors
```