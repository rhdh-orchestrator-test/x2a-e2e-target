---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures system settings, downloads the Chef Automate CLI, deploys the Chef products, and sets up initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:
- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Accepts terms and MLSA agreement

- **Chef Infra Server**: Configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate in the main script

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The deployment scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets the system hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate CLI Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads the Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Resources: curl, gunzip, chmod commands

3. **Chef Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flags

4. **Chef Infra Server Only Deployment** (`setup-automate/deploy-chef-server.sh`):
   - Alternative script that deploys only Chef Infra Server without Chef Automate
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flag

5. **User and Organization Setup** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an initial user with the configured username, name, email, and password
   - Creates an organization and associates the user with it
   - Generates and saves PEM key files for the user and organization validator
   - Resources: chef-server-ctl user-create command, chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None (standalone bash scripts)
**System package dependencies**: curl, gunzip, sudo
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
- **Current storage**: Hardcoded in script variables
- **Usage context**: Used to create the initial Chef user account

## Checks for the Migration

**Files to verify**:
- /etc/hostname (should contain the configured hostname)
- ~/${username}.pem (user key file)
- ~/${orgname}-validator.pem (organization validator key file)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS for Chef Automate UI and Chef Infra Server API)
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

# Chef Automate CLI
which chef-automate
./chef-automate version

# Chef Automate status
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list | grep jtonello
sudo chef-server-ctl org-list | grep lab

# Key files
ls -la ~/jtonello.pem
ls -la ~/lab-validator.pem

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service health
curl -k https://localhost/api/v0/health
curl -k https://localhost/_status

# Logs
sudo journalctl -u chef-automate
sudo chef-automate system-logs

# Chef server API access test (using the generated key)
knife user list -s https://localhost/organizations/lab -u jtonello -k ~/jtonello.pem

# Chef Automate UI access
curl -k -I https://localhost
```