---
source-path: setup-automate
---

Based on my analysis, I don't see any PowerShell files in the setup-automate directory. Instead, I found two Bash shell scripts for deploying Chef Automate and Chef Infra Server on Linux systems. 

Since the request specifically asked for PowerShell code analysis for migration to Ansible, but the repository contains Bash scripts instead, I'll provide a migration plan for these Bash scripts to Ansible.

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations. The scripts are Bash-based, not PowerShell as originally requested.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and/or Chef Infra Server
- Create initial user
- Create initial organization
- Generate and save authentication keys

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
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates initial user and organization
   - Generates authentication key files
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates initial user and organization
   - Generates authentication key files
   - Ansible equivalent: Same modules as above with different parameters

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl \| gunzip > file | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract file |
| chmod +x | ansible.builtin.file | Set file permissions |
| ./chef-automate deploy | ansible.builtin.command | Run Chef Automate CLI |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (scripts are Bash, not PowerShell)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Registry keys**: None (Linux-based deployment)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

**Firewall rules**: None explicitly defined in scripts

## Pre-flight checks:
```
# Check system requirements
ansible all -m shell -a "grep -c processor /proc/cpuinfo" # Should return at least 4
ansible all -m shell -a "free -g | grep Mem | awk '{print \$2}'" # Should return at least 16 (GB)
ansible all -m shell -a "df -h / | grep -v Filesystem | awk '{print \$4}'" # Should have at least 40GB free

# Check network connectivity
ansible all -m uri -a "url=https://packages.chef.io timeout=5"

# Check kernel parameters
ansible all -m shell -a "sysctl vm.max_map_count"
ansible all -m shell -a "sysctl vm.dirty_expire_centisecs"
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace these Bash scripts:

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
      
    - name: Set kernel parameters
      ansible.posix.sysctl:
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        state: present
        sysctl_set: yes
      loop:
        - { key: "vm.max_map_count", value: "262144" }
        - { key: "vm.dirty_expire_centisecs", value: "20000" }
      
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate.gz
      
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate.gz > /tmp/chef-automate
      args:
        creates: /tmp/chef-automate
      
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'
      
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
        creates: /etc/chef-automate/config.toml
      when: deploy_automate | bool
      
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product infra-server --accept-terms-and-mlsa=true
        creates: /etc/chef-automate/config.toml
      when: not deploy_automate | bool
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
      
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: This migration plan addresses Bash scripts rather than PowerShell as originally requested, since the repository contains Bash scripts for Chef Automate deployment.