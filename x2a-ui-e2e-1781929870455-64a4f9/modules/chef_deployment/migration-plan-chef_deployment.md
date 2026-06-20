---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This repository contains two bash scripts for deploying Chef Automate and Chef Infra Server. The scripts set up a Chef infrastructure environment with configurable user and organization settings. There are no actual Chef cookbooks in this repository.

## Service Type and Instances

**Service Type**: Infrastructure Management Server

**Configured Instances**:

- **Chef Automate with Chef Infra Server**: 
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for Automate UI)
  - Key Config: Configurable hostname, user, and organization settings

- **Chef Infra Server (standalone)**:
  - Location/Path: Deployed on the local system
  - Port/Socket: Default ports (443 for Chef Server UI)
  - Key Config: Configurable hostname, user, and organization settings

## File Structure

```
No Chef recipe files found in this repository
No Chef provider files found in this repository
No Chef template files found in this repository
No Chef attribute files found in this repository
```

## Module Explanation

This repository does not contain Chef cookbooks or recipes. Instead, it contains two bash scripts that deploy Chef Automate and Chef Infra Server:

1. **deploy-automate.sh**:
   - Sets the system hostname to the configured value
   - Configures system parameters for optimal Chef Automate performance:
     - vm.max_map_count=262144
     - vm.dirty_expire_centisecs=20000
   - Downloads the Chef Automate CLI tool
   - Deploys Chef Automate and Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a user with the configured username, full name, email, and password
   - Creates an organization with the configured name and associates the created user
   - Generates PEM key files for the user and organization validator

2. **deploy-chef-server.sh**:
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets the system hostname to the configured value
   - Configures the same system parameters
   - Downloads the Chef Automate CLI tool
   - Deploys only Chef Infra Server with the `--accept-terms-and-mlsa=true` flag
   - Creates a user with the configured username, full name, email, and password
   - Creates an organization with the configured name and associates the created user
   - Generates PEM key files for the user and organization validator

Both scripts use the following configurable variables:
- hostname: The hostname for the Chef server (default: 'automate.chef.lab')
- username: Admin username (default: 'jtonello')
- longusername: Full name of the admin user (default: 'John Tonello')
- useremail: Email address for the admin user (default: 'jtonello@chef.lab')
- userpassword: Password for the admin user (default: 'password')
- orgname: Short name for the organization (default: 'lab')
- longorgname: Full name of the organization (default: 'Chef Lab')

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None explicitly installed (Chef Automate handles its dependencies)
**Service dependencies**: None explicitly defined

## Credentials

**Detection Summary**: 1 credential detected across 2 files

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Chef Admin User Password

- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: This password is used for creating the initial admin user in Chef Automate and Chef Infra Server

## Checks for the Migration

**Files to verify**:
- /etc/hosts (should contain the configured hostname)
- /etc/hostname (should be set to the configured hostname)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Service endpoints to check**:
- Ports listening: 443 (Chef Automate UI and Chef Infra Server UI)
- Network interfaces: All interfaces by default

**Templates rendered**:
No templates are rendered by these scripts.

## Pre-flight checks:

```bash
# Hostname configuration
hostname
cat /etc/hostname
cat /etc/hosts | grep $(hostname)

# System parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Chef Automate status (if deployed with deploy-automate.sh)
sudo chef-automate status

# Chef Infra Server status
sudo chef-server-ctl status

# User and organization verification
ls -la *.pem  # Should show user and organization validator PEM files
sudo chef-server-ctl user-list  # Should include the configured username
sudo chef-server-ctl org-list   # Should include the configured organization name

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep 443

# Service status
systemctl status chef-automate  # If using deploy-automate.sh
systemctl status chef-server    # Should be running in both deployment scenarios

# API connectivity test
curl -k https://localhost/organizations  # Should return a list of organizations

# Knife configuration test (requires creating a knife.rb file)
# Create a knife.rb file with:
# node_name 'username'
# client_key 'username.pem'
# chef_server_url 'https://hostname/organizations/orgname'
# Create the .chef directory if it doesn't exist
mkdir -p ~/.chef
# Test knife configuration
knife ssl fetch
knife user list  # Should show the configured user
knife client list  # Should show the organization validator client
```