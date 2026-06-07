---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This is a deployment script for Chef Automate and Chef Infra Server. It sets up a Chef server environment with a single instance, configuring system parameters, installing Chef Automate CLI, deploying Chef products, and creating initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed on the local system alongside Chef Automate
  - Port/Socket: Default ports (443 for API)
  - Key Config: User and organization configuration

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets the system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Products Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server products
   - Accepts terms and MLSA (Master License and Services Agreement)
   - Command: `chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Resources: chef-automate command

4. **User Creation** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials
   - Saves user key to a PEM file
   - Command: `chef-server-ctl user-create $username $longusername $useremail "${userpassword}" --filename $userfilename`
   - Resources: chef-server-ctl command

5. **Organization Creation** (`setup-automate/deploy-automate.sh`):
   - Creates a Chef organization
   - Associates the previously created user with the organization
   - Saves organization validator key to a PEM file
   - Command: `chef-server-ctl org-create $orgname "${longorgname}" --association_user $username --filename $orgfilename`
   - Resources: chef-server-ctl command

The alternative script (`setup-automate/deploy-chef-server.sh`) follows the same pattern but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None (this is a standalone deployment script)
**System package dependencies**: curl, gunzip, bash
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
- /etc/chef-server/
- /etc/chef/
- Generated PEM files: `$username.pem` and `$orgname-validator.pem` in the current directory

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0) by default

**Templates rendered**:
None (deployment script doesn't use templates)

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

# Verify services are running
systemctl status chef-automate
sudo chef-server-ctl service-list

# Check Chef Automate API
curl -k https://localhost/api/v0/auth/version

# Check Chef Infra Server API
curl -k https://localhost/organizations

# Verify user creation
sudo chef-server-ctl user-list | grep $username

# Verify organization creation
sudo chef-server-ctl org-list | grep $orgname

# Check generated credential files
ls -la $username.pem
ls -la $orgname-validator.pem

# Verify web UI access
curl -k -I https://localhost

# Check listening ports
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Check logs
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail

# Verify system resources
free -m
df -h
```