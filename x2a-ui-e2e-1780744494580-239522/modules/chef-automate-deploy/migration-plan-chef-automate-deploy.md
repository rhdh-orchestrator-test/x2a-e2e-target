---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate in the first script, standalone in the second script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys Chef Automate AND Chef Infra Server with `--product automate --product infra-server`
   - Creates a user with the configured username, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures system parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI from packages.chef.io
   - Deploys ONLY Chef Infra Server with `--product infra-server`
   - Creates a user with the configured username, email, and password
   - Creates an organization and associates the user with it
   - Generates PEM files for user authentication and organization validation
   - Resources: sysctl (2), curl (1), chef-automate deploy (1), chef-server-ctl (2)

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
- `/etc/hostname` (should contain the configured hostname)
- `~/${username}.pem` (user authentication key)
- `~/${orgname}-validator.pem` (organization validator key)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate and Chef Infra Server web UIs)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status (for deploy-automate.sh)
sudo chef-automate status
curl -k https://localhost/api/v0/health

# Chef Infra Server status (for both scripts)
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# Authentication verification
knife user list -s https://localhost/organizations/$orgname -u $username -k ~/$userfilename

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Certificate verification
openssl s_client -connect localhost:443 -showcerts

# Log verification
sudo journalctl -u chef-automate
sudo chef-automate logs

# PEM files verification
ls -la ~/$userfilename
ls -la ~/$orgfilename
```