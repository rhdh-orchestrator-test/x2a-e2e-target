---
source-path: setup-automate/deploy-automate.sh
---

Based on my exploration, I notice that the file we're analyzing (deploy-automate.sh) is actually a Bash script, not PowerShell. There doesn't appear to be a PowerShell module named 'chef-automate-deployment' in the repository. However, I'll create a migration plan for converting the Bash script to Ansible, as that seems to be the intent of the request.

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys Chef Automate and Infra Server products, and creates a user and organization in Chef Server.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create a Chef user
- Create a Chef organization and associate the user with it

## File Structure

**Scripts:**
setup-automate/deploy-automate.sh

**Modules:**
None

**DSC Configurations:**
None

**Data Files:**
None

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for Chef Automate and Chef Infra Server configuration
   - Sets the system hostname
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

## PowerShell to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Chef Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates a Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates a Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (this is a Bash script)
**Windows Features**: None (this is for Linux)
**External packages**: curl, gunzip
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Registry keys**: None (Linux system)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

**Firewall rules**: None explicitly set in the script

## Pre-flight checks:
```
# Check system hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check Chef Automate status
sudo chef-automate status

# Check Chef Infra Server status
sudo chef-server-ctl status

# Verify user creation
sudo chef-server-ctl user-list

# Verify organization creation
sudo chef-server-ctl org-list
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
    - name: Set system hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
    
    - name: Set vm.max_map_count kernel parameter
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        sysctl_set: yes
    
    - name: Set vm.dirty_expire_centisecs kernel parameter
      ansible.posix.sysctl:
        name: vm.dirty_expire_centisecs
        value: '20000'
        state: present
        sysctl_set: yes
    
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate_linux_amd64.zip
    
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate_linux_amd64.zip > chef-automate
      args:
        creates: chef-automate
    
    - name: Set execute permissions on Chef Automate CLI
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

Note: This playbook assumes you have a group of hosts defined as 'chef_servers' in your inventory. You should also consider using Ansible Vault for sensitive information like passwords.