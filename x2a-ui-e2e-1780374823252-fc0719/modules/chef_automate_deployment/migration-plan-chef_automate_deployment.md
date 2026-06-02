---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef_automate_deployment

**TLDR**: This module deploys Chef Automate and Chef Infra Server using bash scripts. It configures a single instance with system settings, downloads and installs Chef Automate CLI, deploys the products, and creates initial user and organization.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: 
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Configured with Chef Infra Server integration

- **Chef Infra Server**:
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Integrated with Chef Automate, configured with initial user and organization

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The module performs operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Extracts and makes the binary executable
   - Deploys Chef Automate with the Infra Server product
   - Accepts terms and MLSA agreement
   - Resources: curl, gunzip, chmod, chef-automate deploy (4)

3. **User and Organization Setup** (`setup-automate/deploy-automate.sh`):
   - Creates initial admin user with specified credentials:
     - Username: jtonello (configurable)
     - Full name: John Tonello (configurable)
     - Email: jtonello@chef.lab (configurable)
     - Password: password (configurable)
     - Saves user key to jtonello.pem
   - Creates initial organization:
     - Org short name: lab (configurable)
     - Org full name: Chef Lab (configurable)
     - Associates admin user with organization
     - Saves validator key to lab-validator.pem
   - Resources: chef-server-ctl user-create (1), chef-server-ctl org-create (1)

The alternative script (`setup-automate/deploy-chef-server.sh`) performs similar operations but only deploys Chef Infra Server without Chef Automate.

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, gunzip, sudo
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
- **Usage context**: Used to create the initial admin user for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- Generated PEM files: jtonello.pem, lab-validator.pem

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**: None (no Chef templates used)

## Pre-flight checks:

```bash
# System configuration
hostname  # Should return automate.chef.lab
cat /proc/sys/vm/max_map_count  # Should return 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should return 20000

# Chef Automate CLI
ls -la ./chef-automate  # Should show executable file
./chef-automate version  # Should show version information

# Chef Automate status
sudo chef-automate status  # Should show all services running
curl -k https://localhost/api/v0/status  # Should return status JSON

# Chef Infra Server status
sudo chef-server-ctl status  # Should show all services running

# User and organization verification
ls -la ./jtonello.pem  # Should show user key file
ls -la ./lab-validator.pem  # Should show validator key file

# Knife configuration test (requires knife client)
# Create a knife.rb file with:
# node_name 'jtonello'
# client_key './jtonello.pem'
# chef_server_url 'https://automate.chef.lab/organizations/lab'
knife ssl check  # Should verify SSL connection
knife user list  # Should show jtonello user
knife org list  # Should show lab organization

# Network listening
sudo netstat -tulpn | grep 443  # Should show services listening on 443
sudo ss -tlnp | grep 443  # Alternative to netstat

# Service status
systemctl list-units --type=service --state=running | grep chef  # Should show Chef services
```