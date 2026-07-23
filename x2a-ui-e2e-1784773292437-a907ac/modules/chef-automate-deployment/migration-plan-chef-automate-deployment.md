---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with user and organization setup. The main features include system configuration, downloading and deploying Chef Automate CLI, and creating initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Includes Chef Infra Server product

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Deployed alongside Chef Automate
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username: configurable (default: 'jtonello')
     - Full name: configurable (default: 'John Tonello')
     - Email: configurable (default: 'jtonello@chef.lab')
     - Password: configurable (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name: configurable (default: 'lab')
     - Full name: configurable (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef/
- Generated PEM files: jtonello.pem, lab-validator.pem (or as configured)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (deployment uses CLI tools rather than templates)

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

# Verify Chef Automate UI is accessible
curl -k https://localhost/api/v0/auth/version

# Verify Chef Infra Server API is accessible
curl -k https://localhost/organizations

# Check user creation
sudo chef-server-ctl user-list | grep jtonello

# Check organization creation
sudo chef-server-ctl org-list | grep lab

# Verify PEM files exist and have correct permissions
ls -la jtonello.pem
ls -la lab-validator.pem

# Check Chef Automate services
sudo systemctl status chef-automate

# Check logs
sudo journalctl -u chef-automate -f
sudo chef-server-ctl tail

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Verify Chef Automate UI is accessible in a browser
echo "Open https://$(hostname) in a browser and verify you can log in with the configured credentials"
```