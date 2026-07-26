---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Setup

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys the Chef Automate and Infra Server products, and creates a user and organization in the Chef Server.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management)

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server
- Creating a user in Chef Server
- Creating an organization in Chef Server and associating the user

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None

**DSC Configurations:**
None

**Data Files:**
None

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets up variables for hostname, user details, and organization details
   - Sets the hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

## PowerShell to Ansible Mapping

Note: The original script is in Bash, not PowerShell. Here's the mapping to Ansible:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates a user in Chef Server |
| chef-server-ctl org-create | ansible.builtin.command | Creates an organization in Chef Server |

## Dependencies

**PowerShell Module dependencies**: None (original is Bash)
**Windows Features**: None (runs on Linux)
**External packages**: Chef Automate CLI
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Registry keys**: None (Linux system)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: 
- Port 443 (HTTPS) for Chef Automate web UI
- Port 9631 for Chef Habitat Supervisor

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb"
ansible all -m setup -a "filter=ansible_processor_vcpus"

# Check disk space
ansible all -m shell -a "df -h"

# Check if Chef Automate is already installed
ansible all -m shell -a "which chef-automate || echo 'Not installed'"

# Check if Chef Server is already installed
ansible all -m shell -a "which chef-server-ctl || echo 'Not installed'"
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
    
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: 
        cmd: gunzip -c /tmp/chef-automate.gz > chef-automate
        creates: chef-automate
    
    - name: Set execute permissions on Chef Automate CLI
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
    
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
        creates: /hab
    
    - name: Create user in Chef Server
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
    
    - name: Create organization in Chef Server
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: The original script is a Bash script, not PowerShell. The migration plan provides guidance on how to convert this Bash script to Ansible, which is what I believe you're looking for based on your requirements.