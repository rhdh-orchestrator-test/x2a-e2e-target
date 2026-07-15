---
source-path: setup-automate
---

# Migration Plan: Chef Deployment Scripts

**TLDR**: The repository contains Bash scripts for deploying Chef Automate and Chef Infra Server on Linux systems. There are no PowerShell scripts or modules found in the repository, specifically no 'chef-deployment' PowerShell module. The migration to Ansible would involve converting these Bash scripts to Ansible playbooks for Linux-based Chef server deployment.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating Chef user accounts
- Creating Chef organizations
- Generating and storing authentication keys

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
No PowerShell modules found.

**DSC Configurations:**
No DSC configurations found.

**Data Files:**
No configuration data files found.

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate)
   - Creates a Chef user
   - Creates a Chef organization
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

## PowerShell to Ansible Mapping

Since there are no PowerShell scripts to migrate, here's the mapping for the Bash commands to Ansible modules:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl | ansible.builtin.get_url | Downloads files |
| chmod | ansible.builtin.file | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (no PowerShell scripts)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Registry keys**: None (Linux-based deployment)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: None explicitly defined in scripts

## Pre-flight checks:
```
# Check hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check Chef Automate status
sudo ./chef-automate status

# Verify Chef user
sudo chef-server-ctl user-list

# Verify Chef organization
sudo chef-server-ctl org-list
```

## Note on Migration Request

The request mentioned analyzing a 'chef-deployment' PowerShell module, but no such module was found in the repository. The repository contains Bash scripts for deploying Chef on Linux systems, not PowerShell scripts for Windows. The migration to Ansible would involve creating playbooks for Linux-based Chef server deployment rather than converting PowerShell to Ansible.