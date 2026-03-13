# Migration Plan: Chef Server Deployment Script

**TLDR**: This is a Bash script that deploys Chef Infra Server (without Chef Automate) on a VM. It sets up the server, creates an initial admin user, and creates an organization. The script is not a Chef cookbook but a shell script that installs and configures Chef Server.

## Service Type and Instances

**Service Type**: Configuration Management Server (Chef Infra Server)

**Configured Instances**:

- **Chef Infra Server**: Single instance deployment of Chef Infra Server
  - Location/Path: Default installation path (managed by chef-automate CLI)
  - Port/Socket: 443 (HTTPS)
  - Key Config: 
    - Hostname: Configurable (default: 'automate.chef.lab')
    - Initial admin user with configurable username/password
    - Initial organization with configurable name

## File Structure

```
setup-automate/deploy-chef-server.sh
```

This is not a Chef cookbook but a Bash script that deploys Chef Infra Server. There are no recipe files, providers, templates, or attribute files as would be found in a Chef cookbook structure.

## Module Explanation

The script performs operations in this order:

1. **Set Variables** (`setup-automate/deploy-chef-server.sh`):
   - Defines configurable variables for Chef Server deployment:
     - hostname: 'automate.chef.lab'
     - username: 'jtonello'
     - longusername: 'John Tonello'
     - useremail: 'jtonello@chef.lab'
     - userpassword: 'password'
     - orgname: 'lab'
     - longorgname: 'Chef Lab'
   - Defines dynamic variables:
     - userfilename: "${username}.pem"
     - orgfilename: "${orgname}-validator.pem"

2. **Configure System** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Resources: hostnamectl, sysctl (2)

3. **Install Chef Automate CLI** (`setup-automate/deploy-chef-server.sh`):
   - Downloads chef-automate CLI tool
   - Makes it executable
   - Resources: curl, chmod

4. **Deploy Chef Infra Server** (`setup-automate/deploy-chef-server.sh`):
   - Runs chef-automate deploy with infra-server product
   - Accepts terms and MLSA
   - Resources: chef-automate CLI

5. **Create Admin User** (`setup-automate/deploy-chef-server.sh`):
   - Creates initial admin user with chef-server-ctl
   - Saves user key to file (e.g., jtonello.pem)
   - Resources: chef-server-ctl

6. **Create Organization** (`setup-automate/deploy-chef-server.sh`):
   - Creates organization with chef-server-ctl
   - Associates admin user with organization
   - Saves organization validator key to file (e.g., lab-validator.pem)
   - Resources: chef-server-ctl

## Dependencies

**External dependencies**: None specified in the script
**System package dependencies**: None explicitly installed (relies on base system)
**Service dependencies**: 
- Requires sufficient system resources for Chef Server
- Requires network connectivity for downloading chef-automate CLI

## Checks for the Migration

**Files to verify**:
- User key file: `${username}.pem` (e.g., jtonello.pem)
- Organization validator key: `${orgname}-validator.pem` (e.g., lab-validator.pem)
- Chef Server configuration files (installed by chef-automate)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Web UI: https://{hostname}

**Templates rendered**:
None (this is a shell script, not a Chef cookbook)

## Pre-flight checks:
```bash
# System configuration
hostname
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Server status
sudo chef-server-ctl status
sudo chef-server-ctl service-list

# User verification
sudo chef-server-ctl user-list
sudo chef-server-ctl user-show jtonello  # Replace with actual username

# Organization verification
sudo chef-server-ctl org-list
sudo chef-server-ctl org-show lab  # Replace with actual org name

# Key files
ls -la jtonello.pem  # Replace with actual username
ls -la lab-validator.pem  # Replace with actual org name

# Network listening
sudo netstat -tulpn | grep ':443'
sudo ss -tlnp | grep ':443'

# Web UI access
curl -k https://localhost/_status
curl -k https://automate.chef.lab/_status  # Replace with actual hostname

# Chef Server API access (using keys)
knife user list -c /etc/chef/client.rb -k jtonello.pem -u jtonello  # Replace with actual username/key

# Log files
sudo tail -f /var/log/chef-server/nginx/access.log
sudo tail -f /var/log/chef-server/nginx/error.log
sudo tail -f /var/log/chef-server/bookshelf/current

# Service status
sudo systemctl status chef-server
```