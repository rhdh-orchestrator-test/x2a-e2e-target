---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This module consists of two bash scripts for deploying Chef Automate and Chef Infra Server on a VM. The scripts configure system settings, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with user and organization settings

- **Chef Infra Server**: Configuration management server
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Configured with user and organization settings

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (default: 'automate.chef.lab')
   - Configures system kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a user with the specified username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: system commands (hostnamectl, sysctl), curl, file operations, chef-automate CLI, chef-server-ctl

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

### User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- `/etc/hostname` - Should contain the configured hostname
- `chef-automate` executable in the current directory
- User PEM file (e.g., `jtonello.pem`) in the current directory
- Organization validator PEM file (e.g., `lab-validator.pem`) in the current directory

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered in these scripts.

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

# User and organization verification
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list  # Should include the configured organization name

# PEM files existence and permissions
ls -la ${username}.pem  # Should exist with appropriate permissions
ls -la ${orgname}-validator.pem  # Should exist with appropriate permissions

# Network listening
netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
ss -tlnp | grep 443

# Web UI accessibility
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/_status  # Should return status information

# API accessibility (using the generated PEM file)
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ${username}.pem --no-editor  # Should list users

# Log verification
sudo journalctl -u chef-automate  # Check for any errors
sudo chef-automate logs  # View Chef Automate logs

# System resources
df -h  # Check disk space
free -m  # Check memory usage
top -n 1  # Check CPU usage
```