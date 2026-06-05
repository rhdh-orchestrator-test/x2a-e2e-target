---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This is a bash script for deploying Chef Automate and Chef Infra Server on a VM. It configures system settings, downloads the Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (typically 443)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

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
   - Resources: curl, chmod, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

Note: The `setup-automate/deploy-chef-server.sh` script is similar but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (this is a bash script, not a Chef cookbook)
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `jtonello.pem` (or configured username.pem) - User key file
- `lab-validator.pem` (or configured orgname-validator.pem) - Organization validator key file

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None (this is a bash script, not a Chef cookbook with templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# Verify Chef user
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl user-show jtonello  # Replace with configured username

# Verify Chef organization
sudo chef-server-ctl org-list  # Should include the configured organization name
sudo chef-server-ctl org-show lab  # Replace with configured organization name

# Verify key files
ls -la jtonello.pem  # Replace with configured username.pem
ls -la lab-validator.pem  # Replace with configured orgname-validator.pem

# Check web UI accessibility
curl -k https://localhost  # Should return Chef Automate login page
curl -I -k https://localhost  # Should return HTTP 200 OK

# Check services
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Check logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Network listening
sudo netstat -tulpn | grep 443
sudo ss -tlnp | grep 443

# Disk space
df -h /var/opt/chef-automate  # Check disk space for Chef Automate
df -h /var/opt/opscode  # Check disk space for Chef Infra Server
```