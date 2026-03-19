# Migration Plan: Chef Automate Deployment

**TLDR**: This is a simple bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Main automation platform for Chef
  - Location/Path: Installed via Chef Automate CLI
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed via Chef Automate CLI
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
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates a Chef organization:
     - Short name: lab (configurable)
     - Full name: Chef Lab (configurable)
     - Associates the created user with the organization
     - Saves organization validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

Note: The `setup-automate/deploy-chef-server.sh` script is nearly identical but only deploys the Chef Infra Server component without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (this is a standalone bash script)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/chef/jtonello.pem (user key)
- /etc/chef/lab-validator.pem (organization validator key)
- chef-automate executable in the deployment directory

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (bash script with variables)

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
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
sudo chef-server-ctl org-show lab

# Key files
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI access
curl -k https://automate.chef.lab/api/_status
curl -k https://automate.chef.lab/api/v0/health

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service processes
ps aux | grep chef-server
ps aux | grep automate

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate logs

# Test API access with user key
knife user list -s https://automate.chef.lab/organizations/lab -k jtonello.pem -u jtonello

# Verify organization
knife client list -s https://automate.chef.lab/organizations/lab -k lab-validator.pem
```