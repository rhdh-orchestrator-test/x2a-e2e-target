---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script-based deployment of Chef Automate and Chef Infra Server. It configures a single instance with user and organization setup. The script sets system parameters, downloads Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Default installation path
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the following products:
     - automate (Chef Automate)
     - infra-server (Chef Infra Server)
   - Accepts terms and MLSA automatically
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the following attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Generates user key file: jtonello.pem
   - Creates a Chef organization with the following attributes:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Generates organization validator key: lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

## Dependencies

**External cookbook dependencies**: None (script-based deployment)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef admin user

## Checks for the Migration

**Files to verify**:
- /etc/chef-server/
- /etc/chef/
- Generated PEM files: jtonello.pem, lab-validator.pem

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script-based deployment)

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

# Verify Chef user
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl user-show jtonello

# Verify Chef organization
sudo chef-server-ctl org-list | grep lab
sudo chef-server-ctl org-show lab

# Verify PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test Chef Automate UI access
curl -k https://automate.chef.lab/api/v0/auth/version

# Test Chef Infra Server API access
curl -k https://automate.chef.lab/organizations/lab

# Check services
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Check logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Verify knife connectivity using the generated credentials
knife ssl check -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem
```