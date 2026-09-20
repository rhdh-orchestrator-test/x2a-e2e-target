---
source-path: setup-automate
---

# Migration Plan: setup-automate

**TLDR**: This is NOT a Chef cookbook but rather a collection of shell scripts for deploying Chef Automate and Chef Infra Server infrastructure. It contains two deployment scripts that install and configure Chef management infrastructure on a single VM with one organization and one user.

## Service Type and Instances

**Service Type**: Infrastructure Management Platform (Chef Automate + Chef Infra Server)

**Configured Instances**:

- **Chef Automate + Infra Server** (deploy-automate.sh):
  - Hostname: automate.chef.lab
  - Products: Chef Automate + Chef Infra Server
  - Organization: lab (Chef Lab)
  - User: jtonello (John Tonello)
  - Email: jtonello@chef.lab

- **Chef Infra Server Only** (deploy-chef-server.sh):
  - Hostname: automate.chef.lab
  - Products: Chef Infra Server only
  - Organization: lab (Chef Lab)
  - User: jtonello (John Tonello)
  - Email: jtonello@chef.lab

## File Structure

**CRITICAL ERROR**: This is NOT a Chef cookbook. The execution tree correctly shows "No entry recipe found (expected default.rb)" because this directory contains shell scripts, not Chef cookbook files.

**Actual Files:**
```
deploy-automate.sh
deploy-chef-server.sh
```

**Missing Chef Cookbook Structure:**
- No metadata.rb
- No recipes/ directory
- No attributes/ directory
- No templates/ directory
- No providers/ directory

## Module Explanation

**IMPORTANT**: This is not a Chef cookbook migration but rather a shell script conversion task. The "module" consists of bash scripts that perform Chef infrastructure deployment.

**Script Analysis:**

1. **deploy-automate.sh**:
   - Sets system hostname to 'automate.chef.lab'
   - Configures kernel parameters: vm.max_map_count=262144, vm.dirty_expire_centisecs=20000
   - Downloads chef-automate CLI tool from packages.chef.io
   - Deploys both Chef Automate and Chef Infra Server with auto-acceptance of terms
   - Creates Chef user 'jtonello' with password 'password'
   - Creates Chef organization 'lab' and associates user
   - Generates PEM files: jtonello.pem, lab-validator.pem

2. **deploy-chef-server.sh**:
   - Identical to deploy-automate.sh except deploys only Chef Infra Server (no Automate)
   - Same hostname, user, and organization configuration
   - Same kernel parameter tuning and CLI tool download

## Dependencies

**External dependencies**: 
- Chef Automate CLI (downloaded from packages.chef.io)
- Internet connectivity for package download
- Root/sudo privileges

**System package dependencies**: None (uses pre-built Chef installer)

**Service dependencies**: 
- chef-automate service (managed by installer)
- chef-server services (managed by installer)

## Credentials

**Detection Summary**: 5 credentials detected across 2 files

**Source**:
- **Provider**: Hardcoded
- **URL**: N/A
- **Path**: N/A

### User Password
- **Variable(s)**: `userpassword='password'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Chef user account password for initial setup

### User Email
- **Variable(s)**: `useremail='jtonello@chef.lab'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Chef user account email address

### Username
- **Variable(s)**: `username='jtonello'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Chef user account name

### Organization Name
- **Variable(s)**: `orgname='lab'`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: hardcoded
- **Usage context**: Chef organization identifier

### Generated PEM Files
- **Variable(s)**: `userfilename="${username}.pem"`, `orgfilename="${orgname}-validator.pem"`
- **Source file(s)**: deploy-automate.sh, deploy-chef-server.sh
- **Current storage**: generated files
- **Usage context**: Chef authentication certificates (private keys)

## Checks for the Migration

**Files to verify**:
- deploy-automate.sh
- deploy-chef-server.sh
- /home/[user]/jtonello.pem (user private key)
- /home/[user]/lab-validator.pem (organization validator key)
- /hab/svc/automate-load-balancer/config/ (Chef Automate config)
- /etc/opscode/ (Chef Infra Server config)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS), 80 (HTTP redirect)
- Chef Automate UI: https://automate.chef.lab
- Chef Infra Server API: https://automate.chef.lab/organizations/lab

**Templates rendered**:
None - this uses shell scripts, not Chef templates

## Pre-flight checks:
```bash
# Hostname verification
hostname
hostnamectl status
cat /etc/hostname

# Kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs
cat /proc/sys/vm/max_map_count
cat /proc/sys/vm/dirty_expire_centisecs

# Chef Automate CLI tool
which chef-automate
./chef-automate version
ls -lah chef-automate

# Chef Automate service status (if deployed with Automate)
sudo chef-automate status
sudo hab svc status
systemctl status hab-sup

# Chef Infra Server status
sudo chef-server-ctl status
sudo chef-server-ctl test

# User and organization verification
sudo chef-server-ctl user-list
sudo chef-server-ctl org-list
sudo chef-server-ctl org-show lab
sudo chef-server-ctl user-show jtonello

# PEM file verification
ls -lah jtonello.pem lab-validator.pem
file jtonello.pem lab-validator.pem
openssl rsa -in jtonello.pem -check -noout
openssl rsa -in lab-validator.pem -check -noout

# Web interface accessibility
curl -k -I https://automate.chef.lab
curl -k -I https://automate.chef.lab/organizations/lab
netstat -tulpn | grep :443
netstat -tulpn | grep :80

# API connectivity test
knife ssl check -s https://automate.chef.lab/organizations/lab
knife user list -s https://automate.chef.lab/organizations/lab -u jtonello -k jtonello.pem

# Service logs
sudo journalctl -u hab-sup -f
sudo chef-server-ctl tail
sudo chef-automate logs

# Disk space and system resources
df -h
free -h
ps aux | grep -E "(hab-sup|chef|automate)"

# Network listening services
ss -tlnp | grep -E ":80|:443"
lsof -i :443
lsof -i :80
```