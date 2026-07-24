---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I don't see any PowerShell files in the repository. The files in setup-automate are Bash scripts, not PowerShell. Let me provide a migration plan for converting these Bash scripts to Ansible, as that seems to be the intent of your request.

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations. The scripts are Bash-based, not PowerShell, but can be migrated to Ansible for better infrastructure-as-code practices.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management Platform)

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating initial user accounts
- Creating initial organizations
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
None (no separate configuration data files found)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates an initial user
   - Creates an initial organization
   - Ansible equivalent: Use ansible.builtin.template, ansible.builtin.command, and ansible.builtin.sysctl modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates an initial user
   - Creates an initial organization
   - Ansible equivalent: Use ansible.builtin.template, ansible.builtin.command, and ansible.builtin.sysctl modules

## PowerShell to Ansible Mapping

Note: Since the original scripts are Bash, not PowerShell, I'm providing a Bash-to-Ansible mapping instead:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts files |
| chmod +x | ansible.builtin.file (mode) | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None (no PowerShell modules)
**System requirements**: Linux system with sufficient resources for Chef Automate
**External packages**: Chef Automate CLI
**Service dependencies**: None specified in scripts

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**System parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

**Services to check**:
- Chef Automate services
- Chef Infra Server services

**Network configuration**:
- Hostname resolution for the configured hostname

## Pre-flight checks:
```
# Check system resources
ansible all -m shell -a "free -m"
ansible all -m shell -a "df -h"

# Check network configuration
ansible all -m shell -a "hostname"
ansible all -m shell -a "ping -c 1 $(hostname)"

# Check kernel parameters
ansible all -m shell -a "sysctl vm.max_map_count"
ansible all -m shell -a "sysctl vm.dirty_expire_centisecs"

# Check Chef services after deployment
ansible all -m shell -a "chef-server-ctl status"
ansible all -m shell -a "chef-automate status"
```

## Ansible Playbook Structure

Here's a recommended structure for the Ansible playbook:

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
        dest: /tmp/chef-automate.gz
        
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: 
        cmd: gunzip -c /tmp/chef-automate.gz > /tmp/chef-automate
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

This playbook can be used with an inventory file that defines the `chef_servers` group with the appropriate hosts.