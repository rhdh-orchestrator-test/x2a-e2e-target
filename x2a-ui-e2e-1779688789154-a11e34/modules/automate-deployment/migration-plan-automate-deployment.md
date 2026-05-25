---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures system settings, downloads the Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed on the local system
  - Port/Socket: 443
  - Key Config: Accepts terms and MLSA agreement
  
- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: 443 (shared with Chef Automate)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user with the configured username, full name, email, and password
   - Saves user certificate to a .pem file
   - Creates an organization with the configured name
   - Associates the created user with the organization
   - Saves organization validator certificate to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

4. **Alternative Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Similar to the main script but only deploys Chef Infra Server without Automate
   - Uses the same user and organization setup process
   - Resources: Same as above but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: 
  - setup-automate/deploy-automate.sh
  - setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used for creating the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user certificate file)
- ~/${orgname}-validator.pem (organization validator certificate)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI)
- Network interfaces: All interfaces by default

**Templates rendered**: None (uses direct commands rather than templates)

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
sudo chef-server-ctl user-list | grep $(hostname)

# Organization verification
sudo chef-server-ctl org-list | grep lab

# Certificate files
ls -la ~/*.pem

# Network listening
netstat -tulpn | grep 443
curl -k https://localhost/api/v0/health

# Service status
systemctl status chef-automate
```