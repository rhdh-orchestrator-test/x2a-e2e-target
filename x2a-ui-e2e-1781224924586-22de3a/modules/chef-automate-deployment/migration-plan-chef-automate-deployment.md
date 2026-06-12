---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a simple bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate CLI, deploys Chef Automate and Chef Infra Server, and creates a user and organization.

## Service Type and Instances

**Service Type**: Configuration Management Platform

**Configured Instances**:
- **Chef Automate**: A platform for continuous automation that includes Chef Infra, Chef InSpec, and Chef Habitat
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA

- **Chef Infra Server**: The server component of Chef Infra
  - Location/Path: Deployed on the local system
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
   - Sets the hostname to the value specified in the `hostname` variable
   - Configures kernel parameters for optimal performance:
     - Sets vm.max_map_count=262144
     - Sets vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Resources: curl, gunzip, chmod, chef-automate deploy

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates a user with the following attributes:
     - Username: Value of `username` variable
     - Full name: Value of `longusername` variable
     - Email: Value of `useremail` variable
     - Password: Value of `userpassword` variable
     - Saves user key to a file named after the username with .pem extension
   - Creates an organization with the following attributes:
     - Short name: Value of `orgname` variable
     - Full name: Value of `longorgname` variable
     - Associates the previously created user with the organization
     - Saves organization validator key to a file named after the organization with -validator.pem extension
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate has its own dependencies

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user for authentication to Chef Infra Server and Chef Automate

## Checks for the Migration

**Files to verify**:
- `/etc/chef/` directory and contents
- User PEM file (e.g., `jtonello.pem`)
- Organization validator PEM file (e.g., `lab-validator.pem`)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and API)
- Network interfaces: All interfaces by default

**Templates rendered**: None (bash script doesn't use templates)

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
sudo chef-server-ctl user-list | grep $(grep username= setup-automate/deploy-automate.sh | cut -d"'" -f2)

# Verify organization creation
sudo chef-server-ctl org-list | grep $(grep orgname= setup-automate/deploy-automate.sh | cut -d"'" -f2)

# Check PEM files
ls -la $(grep username= setup-automate/deploy-automate.sh | cut -d"'" -f2).pem
ls -la $(grep orgname= setup-automate/deploy-automate.sh | cut -d"'" -f2)-validator.pem

# Verify Chef Automate UI is accessible
curl -k https://localhost/api/v0/auth/version

# Check services are running
sudo systemctl status chef-automate
sudo systemctl status chef-server

# Check ports are listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Check logs
sudo journalctl -u chef-automate -n 50
sudo journalctl -u chef-server -n 50

# Verify API access with the created user
knife user list -s https://localhost/organizations/$(grep orgname= setup-automate/deploy-automate.sh | cut -d"'" -f2) -u $(grep username= setup-automate/deploy-automate.sh | cut -d"'" -f2) -k $(grep username= setup-automate/deploy-automate.sh | cut -d"'" -f2).pem
```