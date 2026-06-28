---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys Chef Automate and Infra Server products, and creates a user and organization in Chef Server. The script is actually a Bash script, not PowerShell, so we'll be migrating from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create a Chef user
- Create a Chef organization and associate it with the user

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
   - Sets variables for Chef Automate and Chef Infra Server configuration
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and prepares the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates it with the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

## PowerShell to Ansible Mapping

Note: Since the original script is Bash, not PowerShell, we're mapping Bash commands to Ansible modules:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl | ansible.builtin.get_url | Downloads files from URLs |
| gunzip/chmod | ansible.builtin.command | Processes downloaded files |
| chef-automate deploy | ansible.builtin.command | Runs Chef Automate CLI commands |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (This is a Bash script)
**External packages**: Chef Automate CLI
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- User PEM file (created by chef-server-ctl user-create)
- Organization validator PEM file (created by chef-server-ctl org-create)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check if Chef Automate is running
chef-automate status

# Check if Chef Infra Server is running
chef-server-ctl status

# Verify user creation
chef-server-ctl user-list

# Verify organization creation
chef-server-ctl org-list
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace the Bash script:

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
    
    - name: Extract and prepare Chef Automate CLI
      ansible.builtin.shell: |
        gunzip -c /tmp/chef-automate.gz > chef-automate
        chmod +x chef-automate
      args:
        creates: chef-automate
    
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command: >
        ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        creates: /hab
    
    - name: Create Chef user
      ansible.builtin.command: >
        chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
    
    - name: Create Chef organization
      ansible.builtin.command: >
        chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```

Note: For security best practices, you should consider using Ansible Vault to encrypt sensitive information like passwords in the actual implementation.