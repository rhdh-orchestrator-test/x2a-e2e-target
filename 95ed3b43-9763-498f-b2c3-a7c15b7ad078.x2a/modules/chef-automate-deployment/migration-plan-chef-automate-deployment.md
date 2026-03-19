# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of Bash scripts that deploy Chef Automate and Chef Infra Server. The scripts configure system settings, download Chef Automate CLI, deploy the products, and create initial users and organizations. No actual Chef cookbooks are used; these are shell scripts that install Chef products.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the main script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname to the configured value
   - Configures the same kernel parameters
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server with `--accept-terms-and-mlsa=true`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None (these are Bash scripts, not Chef cookbooks)
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)
- Chef Automate configuration files (installed by the deployment process)
- Chef Infra Server configuration files (installed by the deployment process)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UIs)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
- No templates are explicitly rendered in these scripts

## Pre-flight checks:
```bash
# System hostname
hostname
cat /etc/hostname

# Kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab

# PEM files existence
ls -la jtonello.pem
ls -la lab-validator.pem

# Web UI accessibility
curl -k https://localhost
curl -k https://automate.chef.lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep https

# Service status
systemctl status chef-automate
systemctl status chef-server

# Logs
sudo journalctl -u chef-automate -f
sudo journalctl -u chef-server -f

# Chef Automate API check (requires token)
# First get a token
TOKEN=$(sudo chef-automate admin-token)
curl -k -H "api-token: $TOKEN" https://localhost/api/v0/auth/version
```