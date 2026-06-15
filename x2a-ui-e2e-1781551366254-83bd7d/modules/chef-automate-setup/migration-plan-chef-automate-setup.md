---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef-automate-setup

**TLDR**: This module consists of two bash scripts that deploy Chef Automate and Chef Infra Server. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Instances

**Service Type**: Application Server (Chef Automate and Chef Infra Server)

**Configured Instances**:

- **Chef Automate**: Chef's enterprise platform for infrastructure automation
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for web UI)
  - Key Config: Hostname, user credentials, organization details

- **Chef Infra Server**: Chef's configuration management server
  - Location/Path: Installed on the local system
  - Port/Socket: Default ports (443 for API)
  - Key Config: Hostname, user credentials, organization details

## File Structure

```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **System Configuration** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Sets hostname to the configured value (default: 'automate.chef.lab')
   - Configures kernel parameters for optimal performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl command, sysctl commands (2)

2. **Chef Automate Installation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Downloads Chef Automate CLI from packages.chef.io
   - Makes the downloaded binary executable
   - Resources: curl command, chmod command

3. **Product Deployment** (`setup-automate/deploy-automate.sh`):
   - Deploys Chef Automate and Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flags

4. **Product Deployment (Infra Server only)** (`setup-automate/deploy-chef-server.sh`):
   - Deploys only Chef Infra Server using the Chef Automate CLI
   - Accepts terms and MLSA agreement
   - Resources: chef-automate deploy command with --product flag

5. **User Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates a user in Chef Infra Server with:
     - Username (default: 'jtonello')
     - Full name (default: 'John Tonello')
     - Email (default: 'jtonello@chef.lab')
     - Password (default: 'password')
   - Saves user key to a .pem file
   - Resources: chef-server-ctl user-create command

6. **Organization Creation** (`setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`):
   - Creates an organization in Chef Infra Server with:
     - Short name (default: 'lab')
     - Full name (default: 'Chef Lab')
   - Associates the previously created user with the organization
   - Saves organization validator key to a .pem file
   - Resources: chef-server-ctl org-create command

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: curl, sudo, hostnamectl, sysctl
**Service dependencies**: None explicitly defined, but requires systemd for service management

## Credentials

**Detection Summary**: 5 credentials detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Infra Server User Password

- **Variable(s)**: `userpassword`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Used to create the initial admin user in Chef Infra Server

### Chef User Authentication Key

- **Variable(s)**: `userfilename` (derived from `username`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated and saved to local file system
- **Usage context**: Authentication key for the created user to access Chef Infra Server

### Chef Organization Validator Key

- **Variable(s)**: `orgfilename` (derived from `orgname`)
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: Generated and saved to local file system
- **Usage context**: Validator key used for bootstrapping nodes to the Chef organization

### Chef User Details

- **Variable(s)**: `username`, `longusername`, `useremail`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: User identity information for Chef Infra Server admin user

### Chef Organization Details

- **Variable(s)**: `orgname`, `longorgname`
- **Source file(s)**: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
- **Current storage**: hardcoded
- **Usage context**: Organization identity information for Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (for hostname configuration)
- /proc/sys/vm/max_map_count (for kernel parameter)
- /proc/sys/vm/dirty_expire_centisecs (for kernel parameter)
- /etc/chef-server (for Chef Server configuration)
- /etc/chef (for Chef client configuration)
- User key file (default: jtonello.pem)
- Organization validator key file (default: lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and API)
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
No templates are rendered in these scripts.

## Pre-flight checks:

```bash
# System configuration checks
hostname
cat /proc/sys/vm/max_map_count  # Should be 262144
cat /proc/sys/vm/dirty_expire_centisecs  # Should be 20000

# Chef Automate CLI check
ls -la ./chef-automate
./chef-automate version

# Chef Automate status check
sudo chef-automate status

# Chef Infra Server status check
sudo chef-server-ctl status

# User and organization verification
sudo chef-server-ctl user-list  # Should include the created user (default: jtonello)
sudo chef-server-ctl org-list  # Should include the created organization (default: lab)

# Key file verification
ls -la ./${username}.pem  # Default: ./jtonello.pem
ls -la ./${orgname}-validator.pem  # Default: ./lab-validator.pem

# Test user authentication
knife user list -s https://localhost/organizations/${orgname} -u ${username} -k ./${username}.pem  # Should succeed and list users

# Service listening check
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Web UI accessibility check
curl -k https://localhost/api/v0/auth/version  # Should return Chef Automate API version
curl -k https://localhost/organizations  # Should return Chef Infra Server organizations

# Logs check
sudo journalctl -u chef-automate -n 50
sudo chef-server-ctl tail

# Chef client configuration test
mkdir -p ~/chef-test
cat > ~/chef-test/knife.rb << EOF
current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "${username}"
client_key               "${current_dir}/${username}.pem"
chef_server_url          "https://${hostname}/organizations/${orgname}"
cookbook_path            ["${current_dir}/cookbooks"]
EOF
cp ./${username}.pem ~/chef-test/
cd ~/chef-test
knife ssl fetch
knife ssl check
knife user list  # Should succeed and list users
```