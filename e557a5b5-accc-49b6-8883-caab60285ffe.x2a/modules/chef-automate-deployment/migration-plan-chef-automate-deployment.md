---
source-path: setup-automate
---

Based on my exploration, I've found that the setup-automate directory contains bash scripts for deploying Chef Automate and Chef Infra Server, not PowerShell scripts. Let me create a migration plan based on these bash scripts instead.

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers the deployment of Chef Automate and Chef Infra Server from bash scripts to Ansible. The scripts configure system settings, download and deploy Chef Automate CLI, and create initial users and organizations in Chef Server.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
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
None

**DSC Configurations:**
None

**Data Files:**
None

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for Chef Automate and Chef Infra Server configuration
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates initial Chef user and organization
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets variables for Chef Infra Server configuration
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates initial Chef user and organization
   - Ansible equivalent: Same modules as above but with different parameters for deployment

## PowerShell to Ansible Mapping

Since the original scripts are in Bash, not PowerShell, here's the Bash to Ansible mapping:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url | Downloads Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets executable permissions |
| chef-automate deploy | ansible.builtin.command | Deploys Chef Automate/Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None
**System packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but likely requires networking and basic system services

## Checks for the Migration

**Files to verify**: 
- /path/to/chef-automate (CLI tool)
- /path/to/[username].pem (user key file)
- /path/to/[orgname]-validator.pem (organization validator key)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb"
ansible all -m setup -a "filter=ansible_processor_vcpus"

# Check if Chef Automate is already installed
ansible all -m stat -a "path=/usr/bin/chef-automate"

# Check if required ports are available
ansible all -m shell -a "ss -tulpn | grep -E '(443|80|9631)'"
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
    userpassword: 'password'
    orgname: 'lab'
    longorgname: 'Chef Lab'
    userfilename: "{{ username }}.pem"
    orgfilename: "{{ orgname }}-validator.pem"
    deploy_automate: true  # Set to false to deploy only Chef Infra Server
    
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
        dest: /tmp/chef-automate.zip
        
    - name: Unzip Chef Automate CLI
      ansible.builtin.unarchive:
        src: /tmp/chef-automate.zip
        dest: /usr/local/bin/
        remote_src: yes
        
    - name: Set executable permissions on Chef Automate CLI
      ansible.builtin.file:
        path: /usr/local/bin/chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: >
          /usr/local/bin/chef-automate deploy 
          {% if deploy_automate %}--product automate {% endif %}
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        creates: /hab  # Prevent re-running if already deployed
      when: deploy_automate
        
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: >
          /usr/local/bin/chef-automate deploy 
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        creates: /hab  # Prevent re-running if already deployed
      when: not deploy_automate
        
    - name: Create Chef user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create 
          {{ username }} {{ longusername }} {{ useremail }} 
          "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create 
          {{ orgname }} "{{ longorgname }}" 
          --association_user {{ username }} 
          --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```