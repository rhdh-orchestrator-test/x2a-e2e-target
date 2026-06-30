---
source-path: setup-automate
---

Based on my analysis, I don't see any PowerShell files in the provided directory. The setup-automate directory contains only two Bash shell scripts for deploying Chef Automate and Chef Infra Server. There is no PowerShell code to migrate to Ansible.

# Migration Plan: Chef Infrastructure Deployment

**TLDR**: This repository contains Bash scripts for deploying Chef Automate and Chef Infra Server on Linux systems. There are no PowerShell scripts to migrate; instead, we need to convert these Bash scripts to Ansible playbooks.

## Service Type and Configuration

**Service Type**: Configuration Management (Chef Server/Automate)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (sysctl)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating Chef user and organization
- Generating and storing authentication keys

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None (No PowerShell modules found)

**DSC Configurations:**
None (No PowerShell DSC configurations found)

**Data Files:**
None (No PowerShell data files found)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Generates authentication key files
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user
   - Generates authentication key files
   - Ansible equivalent: Same modules as above with different parameters

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl \| gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef products |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (No PowerShell code)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- User and organization PEM files (e.g., jtonello.pem, lab-validator.pem)

**Registry keys**: None (Linux-based deployment)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

**Firewall rules**: None explicitly defined in scripts

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_cores"

# Verify hostname resolution
ansible all -m command -a "getent hosts automate.chef.lab"

# Check kernel parameters
ansible all -m command -a "sysctl vm.max_map_count vm.dirty_expire_centisecs"

# Check Chef services after deployment
ansible all -m command -a "chef-server-ctl status"
```