---
source-path: setup-automate
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using shell scripts. It configures a single instance with user and organization setup. The main features include system tuning, downloading and installing Chef Automate CLI, deploying Chef products, and creating initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate Server**: A single instance of Chef Automate server
  - Location/Path: Installed in default locations
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: System tuning parameters (vm.max_map_count=262144, vm.dirty_expire_centisecs=20000)

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed in default locations
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate or standalone depending on script used

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable with chmod +x
   - Resources: curl command, chmod command (2)

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command (1)

   **OR**

   **Chef Infra Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command (1)

4. **User and Organization Setup** (`setup-automate/deploy-automate.sh` or `setup-automate/deploy-chef-server.sh`):
   - Creates a user with the following attributes:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem (derived from username)
   - Creates an organization with the following attributes:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Saves organization validator key to lab-validator.pem (derived from org name)
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: 
  - setup-automate/deploy-automate.sh
  - setup-automate/deploy-chef-server.sh
- **Current storage**: Hardcoded in shell scripts
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- ~/{username}.pem (user key file)
- ~/{orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (no templates used in this cookbook)

## Pre-flight checks:

```bash
# System configuration checks
hostname
cat /etc/hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI check
ls -la ./chef-automate  # Should exist and be executable
./chef-automate version

# Service status checks
systemctl status chef-automate
curl -k https://localhost/api/v0/status  # Chef Automate API status check

# Chef Infra Server checks
systemctl status chef-server
chef-server-ctl status

# User and organization verification
ls -la ~/*.pem  # Should show user and org validator keys
chef-server-ctl user-list  # Should include the created user
chef-server-ctl org-list  # Should include the created organization

# Web UI access check
curl -k -I https://localhost  # Should return HTTP 200 OK

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Log checks
journalctl -u chef-automate -n 50
journalctl -u chef-server -n 50
```