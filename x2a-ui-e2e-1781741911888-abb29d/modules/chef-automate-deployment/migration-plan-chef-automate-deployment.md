---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a bash script-based deployment of Chef Automate and Chef Infra Server. It configures system settings, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
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
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod

3. **Chef Automate and Infra Server Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command

4. **User and Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates a Chef organization with:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

Note: The repository also includes a separate script (`setup-automate/deploy-chef-server.sh`) that deploys only Chef Infra Server without Chef Automate, following a similar process but with the `--product infra-server` flag only.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ./chef-automate (executable binary)
- ./${username}.pem (user key file, default: jtonello.pem)
- ./${orgname}-validator.pem (organization validator key, default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script-based deployment, no templates)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname (default: automate.chef.lab)
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate binary
ls -la ./chef-automate  # Should exist and be executable
./chef-automate version  # Should display version information

# Chef Automate status
sudo ./chef-automate status  # Should show all services running

# Chef Automate UI
curl -k https://localhost  # Should return Chef Automate UI HTML
curl -k https://localhost/api/v0/status  # Should return status JSON

# Chef Infra Server
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
ls -la ./${username}.pem  # Should exist (default: jtonello.pem)
ls -la ./${orgname}-validator.pem  # Should exist (default: lab-validator.pem)

# Test API access with created user
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ./${username}.pem  # Should list the created user

# Network listening
sudo netstat -tulpn | grep 443  # Should show services listening on port 443
sudo ss -tlnp | grep 443  # Alternative check for services on port 443

# Logs
sudo ./chef-automate logs  # Check Chef Automate logs
sudo chef-server-ctl tail  # Check Chef Infra Server logs

# Service status
sudo systemctl status chef-automate  # If systemd service was created
```