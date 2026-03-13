# Migration Plan: Chef Automate Deployment

**TLDR**: This is a simple bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization. There are no actual Chef cookbooks involved, just bash scripts that use the Chef Automate CLI.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Same hostname, integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

There are no Chef cookbooks, recipes, providers, templates, or attributes in this repository. The files are simple bash scripts that use the Chef Automate CLI to deploy Chef Automate and Chef Infra Server.

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname using `hostnamectl`
   - Configures kernel parameters with `sysctl`:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the CLI executable
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Resources: curl, gunzip, chmod, chef-automate CLI

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user with `chef-server-ctl user-create`
     - Username, full name, email, password are configurable
     - Saves user key to a .pem file
   - Creates an organization with `chef-server-ctl org-create`
     - Organization short name and full name are configurable
     - Associates the created user with the organization
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl (2)

The second script (`setup-automate/deploy-chef-server.sh`) is nearly identical but only deploys the Chef Infra Server component without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on existing system packages)
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no Chef templates used)

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

# Verify user creation
sudo chef-server-ctl user-list | grep jtonello

# Verify organization creation
sudo chef-server-ctl org-list | grep lab

# Check if key files exist
ls -la jtonello.pem
ls -la lab-validator.pem

# Verify web UI access
curl -k https://automate.chef.lab/api/_status

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service logs
sudo journalctl -u chef-automate
```