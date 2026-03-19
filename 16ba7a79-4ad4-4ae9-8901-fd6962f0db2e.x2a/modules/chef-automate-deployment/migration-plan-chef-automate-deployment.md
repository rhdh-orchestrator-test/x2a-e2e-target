# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of Bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations. No actual Chef cookbook is present - these are deployment scripts for Chef's own infrastructure components.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module consists of Bash scripts rather than Chef cookbooks. These scripts perform the following operations:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, email, and password
   - Creates an organization and associates the user with it
   - Generates user and organization PEM files
   - Resources: System commands (hostnamectl, sysctl), curl, Chef Automate CLI, Chef Server CLI

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the configured username, email, and password
   - Creates an organization and associates the user with it
   - Generates user and organization PEM files
   - Resources: System commands (hostnamectl, sysctl), curl, Chef Automate CLI, Chef Server CLI

## Dependencies

**External cookbook dependencies**: None (these are deployment scripts, not cookbooks)
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined (Chef Automate handles its own dependencies)

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- User PEM file (e.g., jtonello.pem in the current directory)
- Organization validator PEM file (e.g., lab-validator.pem in the current directory)
- Chef Automate configuration files (created by the deployment process)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0) or as configured by Chef Automate

**Templates rendered**:
- No templates are explicitly rendered by these scripts (Chef Automate handles its own templating)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI access
curl -k https://localhost/api/v0/health

# Service logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs

# Chef server API check
knife user list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem

# Chef Automate UI
echo "Check Chef Automate UI at https://$(hostname)/"
```