---
source-path: setup-automate/deploy-automate.sh
---

Now I'll create a migration plan based on the files I've examined:

# Migration Plan: Chef Automate Setup

**TLDR**: This module deploys Chef Automate and Chef Infra Server on Linux systems. It configures system parameters, downloads and installs Chef Automate, and sets up initial users and organizations. The scripts handle hostname configuration, system tuning, software installation, and initial Chef configuration.

## Service Type and Configuration

**Service Type**: Configuration Management System (Chef Automate/Chef Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters for optimal Chef performance
- Download and install Chef Automate CLI
- Deploy Chef Automate and/or Chef Infra Server
- Create initial Chef user
- Create initial Chef organization
- Generate and save authentication keys

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None (Bash scripts only)

**DSC Configurations:**
None

**Data Files:**
None (Variables are defined within the scripts)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname using `hostnamectl`
   - Configures kernel parameters using `sysctl` for optimal Chef Automate performance
   - Downloads Chef Automate CLI using `curl` and prepares it for execution
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates initial Chef user with admin privileges
   - Creates initial Chef organization and associates the admin user
   - Generates and saves authentication key files
   - Ansible equivalent: Use `ansible.builtin.hostname`, `ansible.posix.sysctl`, `ansible.builtin.get_url`, `ansible.builtin.command`, and custom modules for Chef operations

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets system hostname using `hostnamectl`
   - Configures kernel parameters using `sysctl` for optimal Chef Server performance
   - Downloads Chef Automate CLI using `curl` and prepares it for execution
   - Deploys only Chef Infra Server with acceptance of terms
   - Creates initial Chef user with admin privileges
   - Creates initial Chef organization and associates the admin user
   - Generates and saves authentication key files
   - Ansible equivalent: Same modules as above but with different parameters for Chef Server only

## PowerShell to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Configures kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user (custom module recommended) |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization (custom module recommended) |

## Dependencies

**PowerShell Module dependencies**: None (These are Bash scripts, not PowerShell)
**Linux packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- /etc/sysctl.conf or /etc/sysctl.d/*
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

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

## Ansible Playbook Structure

```yaml
---
- name: Deploy Chef Automate and Infra Server
  hosts: chef_servers
  become: yes
  vars:
    hostname: 'automate.chef.lab'
    username: 'jtonello'
    longusername: 'John Tonello'
    useremail: 'jtonello@chef.lab'
    userpassword: 'password'  # Consider using Ansible Vault for this
    orgname: 'lab'
    longorgname: 'Chef Lab'
    userfilename: "{{ username }}.pem"
    orgfilename: "{{ orgname }}-validator.pem"
    deploy_automate: true  # Set to false to deploy only Chef Infra Server
    
  tasks:
    - name: Set system hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
      
    - name: Configure kernel parameters for Chef
      ansible.posix.sysctl:
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        state: present
        sysctl_set: yes
        reload: yes
      loop:
        - { key: "vm.max_map_count", value: "262144" }
        - { key: "vm.dirty_expire_centisecs", value: "20000" }
        
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate_linux_amd64.zip
        mode: '0644'
        
    - name: Extract Chef Automate CLI
      ansible.builtin.command:
        cmd: gunzip -c /tmp/chef-automate_linux_amd64.zip > chef-automate
        creates: chef-automate
        
    - name: Set executable permissions on Chef Automate CLI
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: >
          ./chef-automate deploy 
          {% if deploy_automate %}--product automate {% endif %}
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        creates: /hab  # Chef Automate creates this directory when installed
      when: deploy_automate
        
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: >
          ./chef-automate deploy 
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        creates: /hab
      when: not deploy_automate
        
    - name: Create Chef user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create 
          {{ username }} 
          {{ longusername | quote }} 
          {{ useremail }} 
          {{ userpassword | quote }} 
          --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create 
          {{ orgname }} 
          {{ longorgname | quote }} 
          --association_user {{ username }} 
          --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```