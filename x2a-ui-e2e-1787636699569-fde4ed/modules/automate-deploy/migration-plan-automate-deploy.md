---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Script

**TLDR**: This is a Bash script (not PowerShell) that deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads Chef Automate CLI, deploys the Chef products, and creates initial user and organization configurations.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management Platform)

**Key Operations**:
- Set system hostname
- Configure kernel parameters for Chef Automate
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create initial user account
- Create initial organization

## File Structure

**IMPORTANT: The file being analyzed is a Bash script, not PowerShell.**

```
setup-automate/deploy-automate.sh
```

**Scripts:**
setup-automate/deploy-automate.sh

**Modules:**
None (This is a Bash script)

**DSC Configurations:**
None (This is a Bash script)

**Data Files:**
None (Configuration is embedded in the script)

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets configurable variables for Chef deployment (hostname, username, organization name, etc.)
   - Sets system hostname using `hostnamectl`
   - Configures kernel parameters using `sysctl` for optimal Chef Automate performance
   - Downloads Chef Automate CLI using `curl`
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates initial user with `chef-server-ctl user-create`
   - Creates initial organization with `chef-server-ctl org-create`
   - Ansible equivalent: Use `ansible.builtin.hostname`, `ansible.posix.sysctl`, `ansible.builtin.get_url`, `ansible.builtin.command`, and custom modules or roles for Chef operations

## PowerShell to Ansible Mapping

**Note: This is a Bash script, not PowerShell. Below is the mapping from Bash commands to Ansible modules:**

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl | ansible.builtin.get_url | Downloads files from URLs |
| chmod | ansible.builtin.file | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None (Bash script)
**System packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: Chef Automate, Chef Infra Server

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
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:

```yaml
- name: Check if Chef Automate is accessible
  uri:
    url: https://{{ hostname }}
    validate_certs: no
    status_code: 200
  register: chef_automate_status
  ignore_errors: yes

- name: Check if Chef Infra Server is accessible
  uri:
    url: https://{{ hostname }}/organizations/{{ orgname }}
    validate_certs: no
    status_code: 200
  register: chef_server_status
  ignore_errors: yes
```

## Ansible Playbook Example

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
    - name: Set system hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
    
    - name: Configure kernel parameters for Chef Automate
      ansible.posix.sysctl:
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        state: present
        reload: yes
      loop:
        - { key: "vm.max_map_count", value: "262144" }
        - { key: "vm.dirty_expire_centisecs", value: "20000" }
    
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

**Note**: This migration plan converts a Bash script to Ansible, not PowerShell to Ansible as originally requested. The file provided was a Bash shell script (.sh), not a PowerShell script (.ps1).