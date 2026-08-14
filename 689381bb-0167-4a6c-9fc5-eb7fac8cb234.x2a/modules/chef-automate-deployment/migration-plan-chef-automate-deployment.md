---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: The provided scripts are actually Bash shell scripts (not PowerShell) that deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download Chef Automate CLI, deploy the Chef products, and create initial users and organizations.

## Service Type and Configuration

**Service Type**: Configuration Management System (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating initial Chef user
- Creating initial Chef organization

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
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and extracts Chef Automate CLI
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates an initial user in Chef Server
   - Creates an initial organization in Chef Server
   - Ansible equivalent: Use ansible.builtin.template, ansible.builtin.command, and ansible.builtin.shell modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Server performance
   - Downloads and extracts Chef Automate CLI
   - Deploys only the Chef Infra Server product
   - Creates an initial user in Chef Server
   - Creates an initial organization in Chef Server
   - Ansible equivalent: Use ansible.builtin.template, ansible.builtin.command, and ansible.builtin.shell modules

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Configures kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef Server user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef Server organization |

## Dependencies

**Module dependencies**: None (not PowerShell)
**System requirements**: Linux system with sufficient resources for Chef Automate/Infra Server
**External packages**: curl, gunzip
**Service dependencies**: None explicitly stated

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**System parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system resources
ansible all -m shell -a "free -m"
ansible all -m shell -a "df -h"

# Check network connectivity
ansible all -m shell -a "curl -s https://packages.chef.io"

# Verify hostname resolution
ansible all -m shell -a "getent hosts {{ hostname }}"
```

## Ansible Playbook Example

Here's a starting point for your Ansible playbook:

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
    
    - name: Configure vm.max_map_count
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        sysctl_set: yes
    
    - name: Configure vm.dirty_expire_centisecs
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
    
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'
    
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
        creates: /etc/chef-automate/config.toml
    
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
    
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: The scripts provided are Bash shell scripts, not PowerShell scripts. The migration plan has been adjusted accordingly to convert from Bash to Ansible rather than PowerShell to Ansible.