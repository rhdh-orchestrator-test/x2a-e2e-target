---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: automate-deploy

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures system settings, downloads Chef Automate CLI, deploys the products, and creates initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in the main script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value using hostnamectl
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Deploys Chef Automate with the automate and infra-server products
   - Accepts terms and MLSA agreement
   - Resources: curl command, chmod command, chef-automate deploy command (3)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user with chef-server-ctl user-create command
     - User attributes: username, full name, email, password
     - Generates user PEM file for authentication
   - Creates an organization with chef-server-ctl org-create command
     - Organization attributes: short name, full name
     - Associates the created user with the organization
     - Generates organization validator PEM file
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command (2)

4. **Alternative Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Similar to the main script but only deploys the Chef Infra Server product
   - Omits the Chef Automate product
   - Otherwise follows the same workflow for system configuration, installation, and user setup
   - Resources: Same as main script but with different chef-automate deploy parameters

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
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
- **Source file(s)**: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial Chef user with chef-server-ctl user-create command

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user PEM file)
- ~/${orgname}-validator.pem (organization validator PEM file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

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
ls -la ~/$userfilename  # Check user PEM file exists

# Organization verification
sudo chef-server-ctl org-list | grep $orgname
ls -la ~/$orgfilename  # Check organization validator PEM file exists

# Service health
curl -k https://localhost/api/_status  # Chef Automate API status
curl -k https://localhost/organizations/$orgname  # Chef Infra Server organization API

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Process verification
ps aux | grep chef-server
ps aux | grep automate

# Log verification
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Authentication test
knife user list -s https://localhost/organizations/$orgname -u $username -k ~/$userfilename

# System resources
free -m
df -h
```