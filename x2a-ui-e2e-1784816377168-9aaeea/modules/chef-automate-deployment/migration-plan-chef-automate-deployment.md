---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I don't see any PowerShell files in the repository. The files in setup-automate are Bash scripts for deploying Chef Automate and Chef Infra Server on Linux systems, not PowerShell scripts for Windows. Let me provide a migration plan based on the Bash scripts instead, as they appear to be the focus of the migration request.

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers converting Bash scripts for deploying Chef Automate and Chef Infra Server to Ansible playbooks. The scripts set system parameters, download Chef Automate CLI, deploy Chef products, and configure users and organizations.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server

**Key Operations**:
- Setting hostname for the Chef server
- Configuring system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating Chef users and organizations
- Generating and storing authentication keys

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None (no PowerShell modules found)

**DSC Configurations:**
None (no PowerShell DSC configurations found)

**Data Files:**
None (no PowerShell data files found)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname for the Chef server
   - Configures system parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates authentication key files
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets hostname for the Chef server
   - Configures system parameters for optimal Chef Server performance
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Generates authentication key files
   - Ansible equivalent: Same modules as above with different parameters

## PowerShell to Ansible Mapping

Since we're dealing with Bash scripts rather than PowerShell, here's the Bash to Ansible mapping:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl \| gunzip > file | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts files |
| chmod +x | ansible.builtin.file | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None (no PowerShell modules)
**System Requirements**: Linux system with sufficient resources for Chef Automate
**External packages**: Chef Automate CLI
**Service dependencies**: None specified in scripts

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**System parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

**Services to check**:
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system resources
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_*"

# Check disk space
ansible all -m shell -a "df -h"

# Verify network connectivity
ansible all -m uri -a "url=https://packages.chef.io timeout=5"

# Check if Chef services are already running
ansible all -m shell -a "systemctl list-units --type=service | grep -i chef"
```

## Ansible Playbook Structure

Here's a suggested structure for the Ansible playbook:

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
    userpassword: 'password'
    orgname: 'lab'
    longorgname: 'Chef Lab'
    userfilename: "{{ username }}.pem"
    orgfilename: "{{ orgname }}-validator.pem"
    deploy_automate: true  # Set to false to deploy only Chef Infra Server
    
  tasks:
    - name: Set hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
      
    - name: Configure system parameters
      ansible.posix.sysctl:
        name: "{{ item.name }}"
        value: "{{ item.value }}"
        state: present
        sysctl_set: yes
      loop:
        - { name: 'vm.max_map_count', value: '262144' }
        - { name: 'vm.dirty_expire_centisecs', value: '20000' }
        
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
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command: >
        ./chef-automate deploy 
        {% if deploy_automate %}--product automate {% endif %}
        --product infra-server 
        --accept-terms-and-mlsa=true
      args:
        creates: /hab
      when: deploy_automate
        
    - name: Deploy Chef Infra Server only
      ansible.builtin.command: >
        ./chef-automate deploy 
        --product infra-server 
        --accept-terms-and-mlsa=true
      args:
        creates: /hab
      when: not deploy_automate
        
    - name: Create Chef user
      ansible.builtin.command: >
        chef-server-ctl user-create 
        {{ username }} {{ longusername }} {{ useremail }} 
        "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command: >
        chef-server-ctl org-create 
        {{ orgname }} "{{ longorgname }}" 
        --association_user {{ username }} 
        --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```

This playbook can be used with a simple inventory file that defines the `chef_servers` group with the appropriate hosts.