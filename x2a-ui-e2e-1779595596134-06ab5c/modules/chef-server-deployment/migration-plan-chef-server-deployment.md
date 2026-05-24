---
source-path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
---

# Migration Plan: Chef Server Deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Infra Server and Chef Automate. The scripts set up a Chef server with a single user and organization, configuring system parameters and installing the necessary components.

## Service Type and Instances

**Service Type**: Application Server (Chef Infra Server and Chef Automate)

**Configured Instances**:

- **Chef Infra Server**: Core Chef server component
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: Single user and organization configuration

- **Chef Automate**: Chef's observability and automation platform (in deploy-automate.sh only)
  - Location/Path: Installed via chef-automate CLI
  - Port/Socket: 443 (HTTPS)
  - Key Config: Integrated with Chef Infra Server

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes it executable
   - Resources: curl, gunzip, chmod

3. **Chef Server Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Deploys Chef Infra Server using the chef-automate CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

4. **Chef Automate Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys both Chef Automate and Chef Infra Server using the chef-automate CLI
   - Accepts terms and MLSA
   - Resources: chef-automate deploy (1)

5. **User and Organization Creation** (`setup-automate/deploy-chef-server.sh` and `setup-automate/deploy-automate.sh`):
   - Creates a Chef user with specified username, name, email, and password
   - Creates a Chef organization with specified name
   - Associates the user with the organization
   - Generates user and organization validator PEM files
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined, but Chef Automate and Chef Infra Server services are installed

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Server Admin Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-chef-server.sh`, `setup-automate/deploy-automate.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /etc/sysctl.conf (for kernel parameter changes)
- /etc/chef-server/
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:

```bash
# Hostname configuration
hostname
cat /etc/hostname

# Kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate CLI
ls -la ./chef-automate
./chef-automate version

# Chef Server status
sudo chef-server-ctl status
curl -k https://localhost/organizations

# Chef Automate status (if deployed)
sudo chef-automate status

# User verification
sudo chef-server-ctl user-list | grep jtonello
ls -la ./jtonello.pem
openssl rsa -in ./jtonello.pem -check -noout

# Organization verification
sudo chef-server-ctl org-list | grep lab
ls -la ./lab-validator.pem
openssl rsa -in ./lab-validator.pem -check -noout

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-server
systemctl status automate

# Log verification
sudo journalctl -u chef-server -n 50
sudo journalctl -u automate -n 50

# API connectivity test
curl -k https://localhost/_status
curl -k -H "Content-Type: application/json" -X GET https://localhost/organizations/lab/users -u jtonello:password

# Disk space
df -h /var/opt/chef-server
df -h /var/opt/chef-automate
```