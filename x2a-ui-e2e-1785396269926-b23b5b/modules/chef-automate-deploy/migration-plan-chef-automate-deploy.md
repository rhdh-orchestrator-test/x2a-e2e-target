---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download the Chef Automate CLI, deploy the Chef products, and configure initial users and organizations. The scripts are Bash-based (not PowerShell) and need to be migrated to Ansible for infrastructure automation.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating initial Chef user
- Creating initial Chef organization
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
None (no separate configuration data files)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets configurable variables for hostname, user details, and organization details
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and prepares the Chef Automate CLI
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates an initial user with the specified credentials
   - Creates an organization and associates the user with it
   - Generates authentication key files
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Contains the same variable configuration and system setup steps
   - Deploys only the Chef Infra Server product
   - Creates the same user and organization configuration
   - Ansible equivalent: Same modules as above with different parameters

## PowerShell to Ansible Mapping

Note: The original scripts are Bash, not PowerShell. Here's the mapping to Ansible:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl \| gunzip > file | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef products |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None (no PowerShell modules)
**System requirements**: Linux system with sufficient resources for Chef Automate
**External packages**: curl, gunzip
**Service dependencies**: None explicitly defined in scripts

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- chef-automate executable (downloaded and made executable)
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)

**Kernel parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

**Services to check**:
- Chef Automate services
- Chef Infra Server services

**Network requirements**:
- Internet access to download Chef Automate CLI
- Proper DNS resolution for the configured hostname

## Pre-flight checks:
```
# Check system resources
ansible.builtin.command: free -m
ansible.builtin.command: df -h

# Check network connectivity
ansible.builtin.uri:
  url: https://packages.chef.io
  
# Check hostname resolution
ansible.builtin.command: getent hosts {{ hostname }}

# Check kernel parameters
ansible.builtin.command: sysctl vm.max_map_count
ansible.builtin.command: sysctl vm.dirty_expire_centisecs
```

## Ansible Playbook Structure

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
    userpassword: 'password'  # Consider using Ansible Vault for passwords
    orgname: 'lab'
    longorgname: 'Chef Lab'
    userfilename: "{{ username }}.pem"
    orgfilename: "{{ orgname }}-validator.pem"
    deploy_automate: true  # Set to false to deploy only Chef Infra Server
    
  tasks:
    - name: Set system hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
        
    - name: Configure kernel parameters for Chef Automate
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
        dest: /tmp/chef-automate_linux_amd64.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.command:
        cmd: gunzip -c /tmp/chef-automate_linux_amd64.zip > chef-automate
        creates: chef-automate
        
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: >
          ./chef-automate deploy 
          {% if deploy_automate %}--product automate {% endif %}
          --product infra-server 
          --accept-terms-and-mlsa=true
        creates: /hab  # Chef Automate installs to /hab by default
      when: deploy_automate | bool
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create 
          {{ username }} {{ longusername }} {{ useremail }} 
          "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create 
          {{ orgname }} "{{ longorgname }}" 
          --association_user {{ username }} 
          --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```