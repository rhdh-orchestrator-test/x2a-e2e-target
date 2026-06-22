---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is not a Chef cookbook but a set of shell scripts that deploy Chef Automate and Chef Infra Server. The scripts configure hostname, system parameters, download and install Chef Automate CLI, deploy Chef products, and create a user and organization.

## Service Type and Instances

**Service Type**: Infrastructure Management Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate Server**: A single instance of Chef Automate server
  - Hostname: Configurable (default: automate.chef.lab)
  - Key Config: Includes Chef Infra Server in deploy-automate.sh
  
- **Chef Infra Server**: A single instance of Chef Infra Server
  - Hostname: Configurable (default: automate.chef.lab)
  - Key Config: Standalone deployment in deploy-chef-server.sh

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Resources: curl, chmod (2)

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

4. **Chef Infra Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

5. **User and Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user with chef-server-ctl user-create
   - Creates an organization with chef-server-ctl org-create
   - Associates the user with the organization
   - Generates PEM files for authentication
   - Resources: chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create a Chef user with chef-server-ctl user-create command

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Chef Automate UI: https://${hostname}
- Chef Infra Server API: https://${hostname}/organizations/${orgname}

**Templates rendered**: None (shell scripts use variables directly)

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

# User verification
sudo chef-server-ctl user-list | grep $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname

# Authentication test
knife user list -s https://$hostname/organizations/$orgname -u $username -k ~/$userfilename

# Web UI access
curl -k https://$hostname

# Generated files
ls -la ~/$userfilename
ls -la ~/$orgfilename

# Service status
systemctl status chef-automate
```