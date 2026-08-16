---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deploy

**TLDR**: This is a bash script that deploys Chef Automate and Chef Infra Server on a VM. It sets up the hostname, system parameters, downloads and installs Chef Automate, and configures a user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: A single instance of Chef Automate server
  - Location/Path: Installed in the default location on the host
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with both automate and infra-server products

- **Chef Infra Server**: A single instance of Chef Infra Server
  - Location/Path: Installed in the default location on the host
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Integrated with Chef Automate

## File Structure

```
setup-automate/deploy-automate.sh
```

## Module Explanation

The script performs operations in this order:

1. **Set Variables** (`setup-automate/deploy-automate.sh`):
   - Sets configuration variables for the deployment:
     - hostname: 'automate.chef.lab'
     - username: 'jtonello'
     - longusername: 'John Tonello'
     - useremail: 'jtonello@chef.lab'
     - userpassword: 'password'
     - orgname: 'lab'
     - longorgname: 'Chef Lab'
   - Sets dynamic variables:
     - userfilename: "${username}.pem"
     - orgfilename: "${orgname}-validator.pem"
   - Resources: Variable declarations (9)

2. **Configure System** (`setup-automate/deploy-automate.sh`):
   - Sets the hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl (1), sysctl (2)

3. **Download and Install Chef Automate** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the binary executable
   - Resources: curl (1), chmod (1)

4. **Deploy Chef Automate and Infra Server** (`setup-automate/deploy-automate.sh`):
   - Runs the Chef Automate deployment with both automate and infra-server products
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

5. **Configure Chef Server User** (`setup-automate/deploy-automate.sh`):
   - Creates a user in Chef Infra Server with:
     - Username: jtonello
     - Full name: John Tonello
     - Email: jtonello@chef.lab
     - Password: password
   - Saves the user key to jtonello.pem
   - Resources: chef-server-ctl user-create (1)

6. **Configure Chef Server Organization** (`setup-automate/deploy-automate.sh`):
   - Creates an organization in Chef Infra Server with:
     - Short name: lab
     - Full name: Chef Lab
   - Associates the previously created user with the organization
   - Saves the organization validator key to lab-validator.pem
   - Resources: chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Server User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user in Chef Infra Server

### Chef Server User Key

- **Variable(s)**: `userfilename="${username}.pem"`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef Infra Server user

### Chef Server Organization Validator Key

- **Variable(s)**: `orgfilename="${orgname}-validator.pem"`
- **Source file(s)**: setup-automate/deploy-automate.sh
- **Current storage**: Generated file
- **Usage context**: Authentication key for the Chef Infra Server organization

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (script doesn't use templates)

## Pre-flight checks:

```bash
# System configuration
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list  # Should include 'jtonello'
ls -la jtonello.pem  # User key should exist

# Organization verification
sudo chef-server-ctl org-list  # Should include 'lab'
ls -la lab-validator.pem  # Organization validator key should exist

# Web UI access
curl -k https://localhost  # Should return Chef Automate login page
curl -k https://localhost/_status  # Should return status information

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate
```