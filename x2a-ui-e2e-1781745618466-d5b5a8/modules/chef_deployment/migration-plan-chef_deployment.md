---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is a simple deployment script for Chef Automate and Chef Infra Server. It consists of two bash scripts that install and configure either Chef Automate with Chef Infra Server or just Chef Infra Server alone, along with creating an initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate with Chef Infra Server**: Deployed via deploy-automate.sh
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Automate UI)
  - Key Config: Creates user and organization with specified credentials

- **Chef Infra Server**: Deployed via deploy-chef-server.sh
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for Chef Server UI)
  - Key Config: Creates user and organization with specified credentials

## File Structure

```
deploy-automate.sh
deploy-chef-server.sh
```

## Module Explanation

The cookbook performs operations in this order:

1. **deploy-automate.sh**:
   - Sets the system hostname to the specified value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

2. **deploy-chef-server.sh**:
   - Sets the system hostname to the specified value
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server with acceptance of terms
   - Creates a user with specified credentials
   - Creates an organization and associates the user with it
   - Resources: hostnamectl, sysctl (2), curl, chef-automate deploy, chef-server-ctl (2)

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
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: Hardcoded in script
- **Usage context**: Used to create the initial Chef user

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should be set to the specified hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate/Infra Server UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
None (scripts don't use templates)

## Pre-flight checks:
```bash
# System configuration
hostname
cat /etc/hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status
sudo chef-automate status

# Chef Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep $username
sudo chef-server-ctl org-list | grep $orgname

# Key files
ls -la ~/${username}.pem
ls -la ~/${orgname}-validator.pem

# Network listening
netstat -tulpn | grep ':443'
ss -tlnp | grep ':443'

# Service health
curl -k https://localhost/api/v0/health

# Logs
sudo journalctl -u chef-automate -n 100
sudo chef-server-ctl tail

# Disk usage
df -h /var/opt/chef-automate
df -h /var/opt/chef-server
```