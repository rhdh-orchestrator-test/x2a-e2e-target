---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Script

**TLDR**: This is a Bash script (not PowerShell) that deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys Chef products, and creates a user and organization in Chef Server.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management Platform)

**Key Operations**:
- Sets hostname for the server
- Configures system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloads and installs Chef Automate CLI
- Deploys Chef Automate and Chef Infra Server products
- Creates a user in Chef Server
- Creates an organization in Chef Server and associates the user with it

## File Structure

**Scripts:**
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh

**Modules:**
None (No PowerShell modules found)

**DSC Configurations:**
None (No PowerShell DSC configurations found)

**Data Files:**
None (No PowerShell data files found)

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for configuration (hostname, username, organization name, etc.)
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys Chef Automate and Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

## PowerShell to Ansible Mapping

Note: This is a Bash script, not PowerShell. Here's the mapping from Bash commands to Ansible modules:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl | ansible.builtin.get_url | Downloads files from URLs |
| chmod | ansible.builtin.file | Sets file permissions |
| chef-automate deploy | ansible.builtin.command | Runs Chef Automate CLI commands |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef Server user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef Server organization |

## Dependencies

**Module dependencies**: None (Bash script, not PowerShell)
**System requirements**: Linux system with sufficient resources for Chef Automate and Chef Infra Server
**External packages**: Chef Automate CLI (downloaded during script execution)
**Service dependencies**: None specified in the script

## Checks for the Migration

**Files to verify**: 
- Chef Automate CLI executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```
# Check system resources
ansible.builtin.command: free -m
ansible.builtin.command: df -h

# Check network connectivity
ansible.builtin.uri:
  url: https://packages.chef.io
  method: GET

# Verify hostname resolution
ansible.builtin.command: getent hosts {{ hostname }}
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replicate the functionality of the Bash script:

```yaml
---
- name: Deploy Chef Automate and Chef Infra Server
  hosts: chef_servers
  become: yes
  vars:
    hostname: 'automate.chef.lab'
    username: 'jtonello'
    longusername: 'John Tonello'
    useremail: 'jtonello@chef.lab'
    userpassword: 'password'
    orgname: 'lab'
    longorgname: 'Chef Lab'
    userfilename: "{{ username }}.pem"
    orgfilename: "{{ orgname }}-validator.pem"
  
  tasks:
    - name: Set hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
    
    - name: Set vm.max_map_count
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        sysctl_set: yes
    
    - name: Set vm.dirty_expire_centisecs
      ansible.posix.sysctl:
        name: vm.dirty_expire_centisecs
        value: '20000'
        state: present
        sysctl_set: yes
    
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate.gz
    
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate.gz > chef-automate
      args:
        creates: chef-automate
    
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
    
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        creates: /hab
    
    - name: Create Chef Server user
      ansible.builtin.command: >
        chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
    
    - name: Create Chef Server organization
      ansible.builtin.command: >
        chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```

Note: This migration plan is based on a Bash script, not PowerShell as originally requested. The script deploys Chef Automate and Chef Infra Server on a Linux system.