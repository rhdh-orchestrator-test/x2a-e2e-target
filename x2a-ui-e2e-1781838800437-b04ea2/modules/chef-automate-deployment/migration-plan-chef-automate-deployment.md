---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using a bash script. It configures system settings, downloads the Chef Automate CLI, deploys the products, and creates a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Deployed to the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: Chef's central server for configuration management
  - Location/Path: Deployed alongside Chef Automate
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment script performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads the Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef user with the configured username, name, email, and password
   - Saves the user's private key to a .pem file
   - Creates a Chef organization with the configured name
   - Associates the created user with the organization
   - Saves the organization validator key to a .pem file
   - Resources: chef-server-ctl user-create, chef-server-ctl org-create (2)

## Dependencies

**External cookbook dependencies**: None (standalone script)
**System package dependencies**: curl, sudo, bash
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected in the deployment script

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account for authentication to Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate CLI
which chef-automate
chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la ~/jtonello.pem
sudo chef-server-ctl user-show jtonello

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la ~/lab-validator.pem
sudo chef-server-ctl org-show lab

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Service health check
curl -k https://localhost/api/v0/health

# Authentication test
export TOKEN=$(curl -sk -H "Content-Type: application/json" -d '{"username":"jtonello", "password":"password"}' https://localhost/api/v0/auth/token | jq -r .token)
curl -sk -H "Authorization: Bearer $TOKEN" https://localhost/api/v0/auth/token/status

# Chef Infra Server API test
knife user list -s https://localhost/organizations/lab -k ~/jtonello.pem -u jtonello

# Logs
sudo journalctl -u chef-automate -n 50
sudo chef-automate system-logs
```