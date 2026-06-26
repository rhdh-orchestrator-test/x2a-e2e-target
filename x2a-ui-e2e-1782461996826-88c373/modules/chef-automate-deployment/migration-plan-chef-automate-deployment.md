---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in one script, standalone in the other

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl command (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the CLI executable
   - Resources: curl command, chmod command (2)

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

4. **Product Deployment (Server Only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy command (1)

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user in Chef Infra Server with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
   - Saves user key to a PEM file
   - Resources: chef-server-ctl user-create command (1)

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an organization in Chef Infra Server with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
   - Associates the previously created user with the organization
   - Saves organization validator key to a PEM file
   - Resources: chef-server-ctl org-create command (1)

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

### Chef Infra Server User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user in Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count
- /proc/sys/vm/dirty_expire_centisecs
- ./chef-automate (CLI tool)
- ./${username}.pem (default: ./jtonello.pem)
- ./${orgname}-validator.pem (default: ./lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no templates used in these scripts)

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname (default: automate.chef.lab)
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should exist and be executable

# Chef Automate status
sudo chef-automate status  # Should show all services running

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User verification
sudo chef-server-ctl user-list  # Should include the created user (default: jtonello)
ls -la ./jtonello.pem  # Should exist (or whatever username was configured)

# Organization verification
sudo chef-server-ctl org-list  # Should include the created organization (default: lab)
ls -la ./lab-validator.pem  # Should exist (or whatever orgname was configured)

# Network listening
sudo netstat -tulpn | grep 443  # Should show services listening on port 443
sudo ss -tlnp | grep 443  # Alternative check for services on port 443

# Web UI access
curl -k https://localhost  # Should return Chef Automate UI content
curl -k https://localhost/_status  # Should return status information

# API access (using the created user key)
knife user list -s https://localhost/organizations/lab -u jtonello -k ./jtonello.pem  # Should list users without errors

# Logs
sudo journalctl -u chef-automate  # Check Chef Automate logs
sudo chef-automate logs  # Alternative way to check Chef Automate logs
```