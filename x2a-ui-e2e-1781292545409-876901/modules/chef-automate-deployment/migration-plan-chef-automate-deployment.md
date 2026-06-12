---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server on a VM. The scripts set system parameters, download and install Chef Automate CLI, deploy the specified products, and create initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Management platform for Chef infrastructure
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef server component
  - Location/Path: Default installation path
  - Port/Socket: 443 (HTTPS)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate deploy command

4. **Product Deployment (Infra Server only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the CLI
   - Accepts terms and MLSA agreement
   - Command: `chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate deploy command

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates initial admin user with specified credentials
   - Saves user key to a PEM file
   - Command: `chef-server-ctl user-create $username $longusername $useremail "${userpassword}" --filename $userfilename`
   - Resources: chef-server-ctl user-create command

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates initial organization
   - Associates the created user with the organization
   - Saves organization validator key to a PEM file
   - Command: `chef-server-ctl org-create $orgname "${longorgname}" --association_user $username --filename $orgfilename`
   - Resources: chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None (standalone scripts)
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- `/etc/chef-server/`
- `/etc/chef/`
- User PEM file (e.g., `jtonello.pem`)
- Organization validator PEM file (e.g., `lab-validator.pem`)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
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

# Verify user and organization
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Verify PEM files
ls -la jtonello.pem
ls -la lab-validator.pem

# Test API access
curl -k https://localhost/organizations/lab

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep chef

# Service health
curl -k https://localhost/_status
curl -k https://localhost/organizations/lab/_status

# Logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Verify Chef server is operational
knife client list -s https://localhost/organizations/lab -u jtonello -k jtonello.pem --no-editor

# Check Chef Automate UI access
curl -k -I https://localhost/
```