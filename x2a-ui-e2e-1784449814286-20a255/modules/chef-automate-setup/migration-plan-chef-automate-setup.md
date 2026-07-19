---
source-path: setup-automate
---

Based on my analysis, I don't see any PowerShell files in the setup-automate directory. Instead, I found two Bash shell scripts that deploy Chef Automate and Chef Infra Server. Since the request specifically asked for PowerShell code analysis for migration to Ansible, but the directory contains Bash scripts, I'll provide a migration plan for these Bash scripts to Ansible instead.

# Migration Plan: Chef Automate and Chef Infra Server Setup Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download and install Chef components, and configure users and organizations. The scripts are Bash-based (not PowerShell) and perform server setup, system configuration, and Chef user/organization management.

## Service Type and Configuration

**Service Type**: Chef Server (Configuration Management)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating Chef users
- Creating Chef organizations
- Associating users with organizations

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
   - Sets hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Sets hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server (without Automate)
   - Creates a Chef user
   - Creates a Chef organization and associates the user
   - Ansible equivalent: Same modules as above but with different parameters for the deploy command

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl \| gunzip > file | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract in two steps |
| chmod +x | ansible.builtin.file | Set file permissions |
| ./chef-automate deploy | ansible.builtin.command | Run Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (scripts are Bash, not PowerShell)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined in scripts

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

**Firewall rules**: None explicitly configured in scripts

## Pre-flight checks:
```
# Check system requirements
ansible all -m shell -a "grep -c processor /proc/cpuinfo" # Should return at least 4
ansible all -m shell -a "free -m | grep Mem | awk '{print $2}'" # Should be at least 16384 (16GB)
ansible all -m shell -a "df -h / | grep -v Filesystem | awk '{print $4}'" # Should have at least 40GB free

# Check network connectivity
ansible all -m uri -a "url=https://packages.chef.io timeout=5"

# Check hostname resolution
ansible all -m shell -a "getent hosts $(hostname)"
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
      
    - name: Configure kernel parameters
      ansible.posix.sysctl:
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        state: present
        sysctl_set: yes
      loop:
        - { key: 'vm.max_map_count', value: '262144' }
        - { key: 'vm.dirty_expire_centisecs', value: '20000' }
      
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate.zip
      
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip < /tmp/chef-automate.zip > chef-automate
      args:
        creates: chef-automate
      
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
      
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command: >
        ./chef-automate deploy 
        --product automate 
        --product infra-server 
        --accept-terms-and-mlsa=true
      args:
        creates: /hab
      when: deploy_automate | bool
      
    - name: Deploy Chef Infra Server only
      ansible.builtin.command: >
        ./chef-automate deploy 
        --product infra-server 
        --accept-terms-and-mlsa=true
      args:
        creates: /hab
      when: not deploy_automate | bool
      
    - name: Create Chef user
      ansible.builtin.command: >
        chef-server-ctl user-create 
        {{ username }} {{ longusername }} {{ useremail }} 
        "{{ userpassword }}" 
        --filename {{ userfilename }}
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

Note: This migration plan addresses Bash scripts rather than PowerShell as requested, since the directory contains only Bash scripts. The Ansible playbook provided would replace the functionality of both Bash scripts, with a variable to control whether to deploy both Chef Automate and Infra Server or just Infra Server.