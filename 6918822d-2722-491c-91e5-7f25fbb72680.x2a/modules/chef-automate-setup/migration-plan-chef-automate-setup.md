# Migration Plan: Chef Automate Setup

**TLDR**: This module consists of Bash scripts that deploy Chef Automate and Chef Infra Server. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the main script, standalone in the secondary script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl command, chmod command, chef-automate deploy command

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Saves the user's private key to a .pem file
   - Creates a Chef organization with the configured name
   - Associates the created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

4. **Chef Infra Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Follows the same pattern but only deploys Chef Infra Server without Chef Automate

## Dependencies

**External cookbook dependencies**: None (these are standalone Bash scripts)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)
- Chef Automate configuration files (in /etc/chef-automate/)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) or specific IP if configured

**Templates rendered**: No templates are rendered by these scripts directly

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the created user
ls -la /path/to/user.pem  # Verify user key exists and has proper permissions

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization
ls -la /path/to/org-validator.pem  # Verify org validator key exists

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
curl -k https://localhost/_status  # Should return status information

# Web UI access
curl -k -I https://localhost/  # Should return HTTP 200 OK

# API access (requires proper authentication)
knife user list -s https://localhost/organizations/ORGNAME -k /path/to/user.pem -u USERNAME
```