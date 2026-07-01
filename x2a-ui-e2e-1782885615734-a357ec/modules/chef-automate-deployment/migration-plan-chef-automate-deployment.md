---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: The scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download and install Chef Automate CLI, deploy Chef products, and configure users and organizations. These are Bash scripts, not PowerShell, so the migration will be from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management System (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create Chef user
- Create Chef organization
- Associate user with organization

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
   - Sets variables for Chef configuration (hostname, username, organization, etc.)
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for Chef configuration
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Same modules as above with different parameters

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url | Downloads Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets executable permissions |
| chef-automate deploy | ansible.builtin.command | Deploys Chef products |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None
**System packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but Chef Automate likely requires database services

## Checks for the Migration

**Files to verify**: 
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```
# Check system requirements
ansible.builtin.command:
  cmd: free -m
  register: memory_check

ansible.builtin.command:
  cmd: df -h
  register: disk_check

# Verify network connectivity
ansible.builtin.uri:
  url: https://packages.chef.io
  status_code: 200

# Check if Chef is already installed
ansible.builtin.stat:
  path: /usr/bin/chef-server-ctl
  register: chef_server_installed
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace the deploy-automate.sh script:

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
        dest: /tmp/chef-automate.zip
        mode: '0644'

    - name: Extract Chef Automate CLI
      ansible.builtin.unarchive:
        src: /tmp/chef-automate.zip
        dest: /tmp/
        remote_src: yes

    - name: Move Chef Automate CLI to working directory
      ansible.builtin.copy:
        src: /tmp/chef-automate
        dest: ./chef-automate
        mode: '0755'
        remote_src: yes

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

Note: This migration plan is based on Bash scripts, not PowerShell as originally requested. The scripts provided are for deploying Chef Automate and Chef Infra Server on Linux systems.