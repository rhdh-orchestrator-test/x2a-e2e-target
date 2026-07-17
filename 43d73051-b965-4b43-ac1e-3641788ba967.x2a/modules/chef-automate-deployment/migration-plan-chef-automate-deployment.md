---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers the conversion of Bash scripts for deploying Chef Automate and Chef Infra Server to Ansible playbooks. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef Automate and/or Chef Infra Server, and create initial user and organization configurations.

## Service Type and Configuration

**Service Type**: Configuration Management System (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server
- Creating initial user account
- Creating initial organization
- Generating and storing authentication keys

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None found

**DSC Configurations:**
None found

**Data Files:**
None found (configuration is embedded in the scripts)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys Chef Automate and Chef Infra Server
   - Creates initial user with specified credentials
   - Creates initial organization and associates the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys only Chef Infra Server
   - Creates initial user with specified credentials
   - Creates initial organization and associates the user
   - Ansible equivalent: Same modules as above but with different parameters for the deployment command

## PowerShell to Ansible Mapping

Note: Since the provided scripts are Bash scripts (not PowerShell), the mapping below shows Bash to Ansible equivalents:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl + gunzip | ansible.builtin.get_url | Downloads files from URLs |
| chmod +x | ansible.builtin.file | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (scripts are Bash)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined in scripts

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- chef-automate executable (downloaded and made executable)
- User PEM file (generated during user creation)
- Organization validator PEM file (generated during org creation)

**Registry keys**: None (Linux-based deployment)

**Services to check**:
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: None explicitly configured in the scripts

## Pre-flight checks:
```
# Check system hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check Chef Automate status (after deployment)
sudo ./chef-automate status

# Verify user and organization creation
ls -la *.pem
```

## Ansible Playbook Structure

Here's a suggested structure for the Ansible playbook:

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
      
    - name: Configure kernel parameters
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
        dest: /tmp/chef-automate.zip
      
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate.zip > chef-automate
      args:
        creates: chef-automate
      
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
      
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command: >
        ./chef-automate deploy 
        {% if deploy_automate %}--product automate {% endif %}
        --product infra-server 
        --accept-terms-and-mlsa=true
      args:
        creates: /hab
      when: deploy_automate
      
    - name: Deploy Chef Infra Server only
      ansible.builtin.command: >
        ./chef-automate deploy 
        --product infra-server 
        --accept-terms-and-mlsa=true
      args:
        creates: /hab
      when: not deploy_automate
      
    - name: Create Chef user
      ansible.builtin.command: >
        chef-server-ctl user-create 
        {{ username }} {{ longusername }} {{ useremail }} 
        "{{ userpassword }}" --filename {{ userfilename }}
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

This playbook includes all the functionality from both Bash scripts, with a variable to control whether to deploy Chef Automate along with Chef Infra Server or just Chef Infra Server alone.