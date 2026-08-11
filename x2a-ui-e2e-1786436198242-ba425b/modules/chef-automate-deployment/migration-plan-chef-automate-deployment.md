---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I don't see any PowerShell files in the repository. The files in setup-automate are Bash scripts, not PowerShell. Let me provide a migration plan for converting these Bash scripts to Ansible, as that seems to be the actual requirement.

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations. The scripts are Bash-based (not PowerShell) and need to be migrated to Ansible playbooks.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting hostname on the target system
- Configuring kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating initial Chef user
- Creating initial Chef organization
- Associating user with organization

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
None (no separate data files found)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Server performance
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Same modules as above with different parameters

## PowerShell to Ansible Mapping

Since the original scripts are Bash and not PowerShell, here's the Bash to Ansible mapping:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl \| gunzip > file | ansible.builtin.get_url | Downloads file with checksum verification |
| chmod +x | ansible.builtin.file | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate CLI |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None (no PowerShell modules)
**System Requirements**: Linux system with sufficient resources for Chef Automate
**External packages**: Chef Automate CLI
**Service dependencies**: None specified in scripts

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Kernel parameters**:
- vm.max_map_count
- vm.dirty_expire_centisecs

**Services to check**:
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system resources
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_count"

# Check if Chef Automate is already installed
ansible all -m stat -a "path=/usr/bin/chef-automate"

# Check if hostname is already set correctly
ansible all -m command -a "hostname"

# Check current kernel parameters
ansible all -m shell -a "sysctl vm.max_map_count vm.dirty_expire_centisecs"
```

## Ansible Playbook Example

Here's a sample Ansible playbook structure for the migration:

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
        dest: /tmp/chef-automate.zip
      
    - name: Unzip Chef Automate CLI
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
      when: deploy_automate | bool
      
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product infra-server --accept-terms-and-mlsa=true
      when: not deploy_automate | bool
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
```

Note: This playbook assumes you're targeting Linux hosts. The original scripts were Bash scripts for Linux, not PowerShell scripts for Windows.