---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and configure initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters with sysctl:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with terms acceptance
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with chef-server-ctl
   - Creates organization and associates admin user
   - Generates and saves user and validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

The second script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Automate:

1. **System Configuration** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters with sysctl:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Infra Server Installation** (`setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys only Chef Infra Server with terms acceptance
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-chef-server.sh`):
   - Creates initial admin user with chef-server-ctl
   - Creates organization and associates admin user
   - Generates and saves user and validator PEM files
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, bash
**Service dependencies**: None (this script installs Chef Automate and Chef Infra Server)

## Credentials

**Detection Summary**: 4 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial admin user for Chef Infra Server

### User Authentication Keys

- **Variable(s)**: `userfilename` (user PEM file), `orgfilename` (organization validator PEM file)
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Generated during deployment and saved to local files
- **Usage context**: Authentication keys for Chef Infra Server API access

## Checks for the Migration

**Files to verify**:
- /etc/hostnamectl (hostname configuration)
- /proc/sys/vm/max_map_count (kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (kernel parameter)
- ${username}.pem (user authentication key)
- ${orgname}-validator.pem (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (bash scripts don't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate installation
chef-automate status
curl -k https://localhost/api/v0/auth/version

# Chef Infra Server installation
chef-server-ctl status
curl -k https://localhost/organizations

# User and organization verification
chef-server-ctl user-list | grep $username
chef-server-ctl org-list | grep $orgname

# Authentication key verification
ls -la ${username}.pem
ls -la ${orgname}-validator.pem

# Service status
systemctl status chef-automate
ss -tlnp | grep ':443'

# Web UI accessibility
curl -k -I https://localhost

# API functionality
knife user list -s https://localhost/organizations/${orgname} -k ${username}.pem -u ${username}
```