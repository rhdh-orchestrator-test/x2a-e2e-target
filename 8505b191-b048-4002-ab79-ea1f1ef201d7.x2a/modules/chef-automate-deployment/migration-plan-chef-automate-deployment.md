---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: The repository contains Bash scripts for deploying Chef Automate and Chef Infra Server on Linux systems, not PowerShell scripts. These scripts set up Chef Automate with user and organization creation. The migration to Ansible would involve creating playbooks to install and configure Chef Automate and Chef Infra Server on Linux hosts.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server
- Creating Chef user accounts
- Creating Chef organizations

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
   - Sets variables for Chef Automate deployment (hostname, username, organization details)
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for Chef Server deployment
   - Sets system hostname using hostnamectl
   - Configures kernel parameters
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server component
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Same modules as above but with different parameters for Chef Server only

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl + gunzip | ansible.builtin.get_url | Downloads files from URLs |
| chmod +x | ansible.builtin.file | Sets file permissions |
| chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None (Bash scripts, not PowerShell)
**System Requirements**: Linux system with sufficient resources for Chef Automate
**External packages**: curl, gunzip
**Service dependencies**: None explicitly defined in scripts

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Kernel parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

**Services to check**:
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system resources
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_count"

# Check if Chef Automate is already installed
ansible all -m stat -a "path=/usr/bin/chef-automate"

# Check kernel parameters
ansible all -m shell -a "sysctl vm.max_map_count vm.dirty_expire_centisecs"
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
    
  tasks:
    - name: Set hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
      
    - name: Set kernel parameter vm.max_map_count
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        sysctl_set: yes
        
    - name: Set kernel parameter vm.dirty_expire_centisecs
      ansible.posix.sysctl:
        name: vm.dirty_expire_centisecs
        value: '20000'
        state: present
        sysctl_set: yes
        
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.unarchive:
        src: /tmp/chef-automate.zip
        dest: /tmp/
        remote_src: yes
        
    - name: Move Chef Automate CLI to working directory
      ansible.builtin.copy:
        src: /tmp/chef-automate
        dest: ./chef-automate
        remote_src: yes
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        creates: /hab
        
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```

Note: The original files are Bash scripts, not PowerShell scripts as initially requested. The migration plan above converts these Bash scripts to Ansible playbooks.