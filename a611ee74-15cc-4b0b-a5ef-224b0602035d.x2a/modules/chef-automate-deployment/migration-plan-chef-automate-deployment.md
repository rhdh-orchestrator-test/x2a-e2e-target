# Migration Plan: Chef Automate Deployment

**TLDR**: This is a simple Bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets system parameters, downloads the Chef Automate CLI, deploys the products, and creates a user and organization. There are no actual Chef cookbooks involved - just Bash scripts that install Chef products.

## Service Type and Instances

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Central management platform for Chef
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Configured with Chef Infra Server product

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Note**: There are no actual Chef cookbooks, recipes, providers, templates, or attribute files in this repository. The scripts are simple Bash scripts that download and install Chef Automate and Chef Infra Server.

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes it executable
   - Deploys Chef Automate with Infra Server product
   - Accepts terms and MLSA
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with:
     - Username, full name, email, password
     - Saves user key to a .pem file
   - Creates a Chef organization with:
     - Organization short name and full name
     - Associates the created user
     - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create

The second script (`setup-automate/deploy-chef-server.sh`) is nearly identical but only deploys the Chef Infra Server product without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: curl, bash
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/chef-automate/config.toml (Chef Automate configuration)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (not a Chef cookbook)

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
ls -la jtonello.pem

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la lab-validator.pem

# Service status
systemctl status chef-automate
ss -tulpn | grep :443

# Web UI access
curl -k https://localhost/api/_status
curl -k https://automate.chef.lab/api/_status

# Chef Server API access
knife user list -s https://automate.chef.lab/organizations/lab -k jtonello.pem -u jtonello

# Logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs
```