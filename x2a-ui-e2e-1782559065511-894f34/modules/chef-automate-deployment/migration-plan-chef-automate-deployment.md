---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate with Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Sets hostname, creates admin user, creates organization

- **Chef Infra Server (standalone)**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Sets hostname, creates admin user, creates organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - URL: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Extracts to local file: chef-automate
     - Makes the file executable
   - Deploys Chef Automate with Infra Server:
     - Command: `chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true`
   - Creates initial admin user:
     - Command: `chef-server-ctl user-create [username] [longusername] [useremail] [userpassword] --filename [userfilename]`
   - Creates initial organization:
     - Command: `chef-server-ctl org-create [orgname] [longorgname] --association_user [username] --filename [orgfilename]`
   - Resources: hostname (1), sysctl (2), download (1), execute (3)

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname to the configured value (e.g., 'automate.chef.lab')
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads Chef Automate CLI:
     - URL: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
     - Extracts to local file: chef-automate
     - Makes the file executable
   - Deploys Chef Infra Server only:
     - Command: `chef-automate deploy --product infra-server --accept-terms-and-mlsa=true`
   - Creates initial admin user:
     - Command: `chef-server-ctl user-create [username] [longusername] [useremail] [userpassword] --filename [userfilename]`
   - Creates initial organization:
     - Command: `chef-server-ctl org-create [orgname] [longorgname] --association_user [username] --filename [orgfilename]`
   - Resources: hostname (1), sysctl (2), download (1), execute (3)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip
**Service dependencies**: None explicitly defined, but requires systemd for service management

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
- /etc/hostname (should contain the configured hostname)
- /proc/sys/vm/max_map_count (should be 262144)
- /proc/sys/vm/dirty_expire_centisecs (should be 20000)
- ~/[username].pem (admin user key file)
- ~/[orgname]-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate/Infra Server web UI)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: No templates are rendered in these scripts.

## Pre-flight checks:
```bash
# System configuration
hostname  # Should match the configured hostname
sysctl vm.max_map_count  # Should be 262144
sysctl vm.dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI
ls -la ~/chef-automate  # Should exist and be executable
~/chef-automate version  # Should show version information

# Service status
systemctl status chef-automate  # Should be active (running)

# For Chef Automate with Infra Server deployment
curl -k https://localhost/api/v0/auth/version  # Should return Chef Automate API version
curl -k https://localhost/organizations  # Should return Chef Infra Server organizations

# For Chef Infra Server only deployment
curl -k https://localhost/organizations  # Should return Chef Infra Server organizations

# User and organization verification
ls -la ~/$userfilename  # Should exist (admin user key)
ls -la ~/$orgfilename  # Should exist (organization validator key)

# Chef Infra Server CLI verification
sudo chef-server-ctl user-list  # Should include the created admin user
sudo chef-server-ctl org-list  # Should include the created organization

# Network listening
sudo netstat -tulpn | grep 443  # Should show Chef Automate/Infra Server listening
sudo ss -tlnp | grep 443  # Alternative check for listening ports

# Logs
sudo journalctl -u chef-automate -n 50  # Check recent logs
sudo chef-automate system-logs  # Check Chef Automate system logs
```