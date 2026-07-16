---
source-path: setup-automate/deploy-automate.sh
---

Now I'll create a detailed migration plan based on these files:

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers the conversion of Bash scripts for deploying Chef Automate and Chef Infra Server to Ansible. The scripts set up the hostname, system parameters, download Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters for optimal performance
- Download and install Chef Automate CLI
- Deploy Chef Automate and/or Chef Infra Server
- Create initial admin user
- Create initial organization
- Generate and store authentication keys

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
   - Sets configurable variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and extracts the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates an initial admin user with the specified details
   - Creates an organization and associates the admin user with it
   - Generates and saves authentication key files
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Contains the same variable configuration and system setup steps
   - Deploys only the Chef Infra Server product
   - Creates the same user and organization structure
   - Ansible equivalent: Same modules as above with different parameters

## PowerShell to Ansible Mapping

Note: These are actually Bash scripts, not PowerShell, so I'm mapping Bash commands to Ansible modules:

| Bash Command/Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Bash dependencies**: None explicit
**System requirements**: Linux with sufficient resources for Chef Automate
**External packages**: curl, gunzip
**Service dependencies**: None explicit

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- chef-automate executable in the working directory
- User key file (e.g., jtonello.pem)
- Organization validator key file (e.g., lab-validator.pem)

**Kernel parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

**Services to check**:
- Chef Automate services
- Chef Infra Server services

**Firewall rules**:
- Ports for Chef Automate (443)
- Ports for Chef Infra Server (443)

## Pre-flight checks:
```
# Check system resources
ansible.builtin.command: free -m
ansible.builtin.command: df -h

# Check network connectivity
ansible.builtin.uri:
  url: https://packages.chef.io
  status_code: 200

# Check hostname resolution
ansible.builtin.command: getent hosts {{ hostname }}
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
    userpassword: 'password'  # Consider using Ansible Vault for this
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
        dest: /tmp/chef-automate_linux_amd64.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip < /tmp/chef-automate_linux_amd64.zip > chef-automate
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
      when: deploy_automate | bool
      args:
        creates: /hab
        
    - name: Deploy Chef Infra Server only
      ansible.builtin.command: >
        ./chef-automate deploy 
        --product infra-server 
        --accept-terms-and-mlsa=true
      when: not deploy_automate | bool
      args:
        creates: /hab
        
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