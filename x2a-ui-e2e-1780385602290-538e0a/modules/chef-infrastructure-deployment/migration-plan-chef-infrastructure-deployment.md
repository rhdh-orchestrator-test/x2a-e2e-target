---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure either Chef Automate with Chef Infra Server or just Chef Infra Server alone. The scripts set up a single instance with configurable user and organization details.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Chef Automate UI)
  - Key Config: Custom hostname, user, and organization settings

- **Chef Infra Server (standalone)**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Chef Server UI)
  - Key Config: Custom hostname, user, and organization settings

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: sysctl (2), curl/gunzip (1), chef-automate deploy (1), chef-server-ctl (2)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI tool
   - Deploys only Chef Infra Server (without Automate) with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Generates PEM key files for user and organization
   - Resources: sysctl (2), curl/gunzip (1), chef-automate deploy (1), chef-server-ctl (2)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
**Service dependencies**: None explicitly defined (Chef Automate handles its own dependencies)

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: 
  - setup-automate/deploy-automate.sh
  - setup-automate/deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Chef Server UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System hostname check
hostname
cat /etc/hostname

# Kernel parameter checks
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status (for deploy-automate.sh)
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User verification
sudo chef-server-ctl user-list | grep $username

# Organization verification
sudo chef-server-ctl org-list | grep $orgname

# Key file verification
ls -la ~/${username}.pem
ls -la ~/${orgname}-validator.pem

# Service connectivity
curl -k https://localhost/api/_status

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Process verification
ps aux | grep chef-server
ps aux | grep automate

# Log verification
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail

# Disk space
df -h /var/opt/chef-automate
df -h /var/opt/opscode

# Memory usage
free -m
```