---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization. The script is not a Chef cookbook but a shell script that installs Chef products.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's central server for configuration management
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl to the value specified in the hostname variable
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts the binary and makes it executable
   - Deploys Chef Automate and Chef Infra Server with the --accept-terms-and-mlsa flag
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with chef-server-ctl user-create command
     - Username, full name, email, and password are specified in variables
     - Generates a user key file (e.g., jtonello.pem)
   - Creates a Chef organization with chef-server-ctl org-create command
     - Organization short name and full name are specified in variables
     - Associates the created user with the organization
     - Generates an organization validator key file (e.g., lab-validator.pem)
   - Resources: chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None (this is a shell script, not a Chef cookbook)
**System package dependencies**: curl, gunzip, sudo
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
- **Usage context**: Used to create the initial Chef user account with chef-server-ctl user-create command

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (this is a shell script, not a Chef cookbook with templates)

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

# Verify user creation
sudo chef-server-ctl user-list  # Should include the created user
ls -la /path/to/user/key/file.pem  # Verify user key file exists

# Verify organization creation
sudo chef-server-ctl org-list  # Should include the created organization
ls -la /path/to/org/validator/key/file.pem  # Verify organization validator key file exists

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate and Chef Infra Server listening
curl -k https://localhost  # Should return Chef Automate login page

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Service health
sudo chef-automate service-versions
```