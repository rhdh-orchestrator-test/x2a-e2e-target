---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: The scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download and install Chef components, and configure users and organizations. These are Bash scripts, not PowerShell scripts, so the migration will be from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server
- Creating Chef user accounts
- Creating Chef organizations

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
   - Sets variables for Chef configuration (hostname, username, organization name, etc.)
   - Sets the system hostname
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for Chef configuration
   - Sets the system hostname
   - Configures kernel parameters
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Same modules as above but with different parameters for the deployment command

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl \| gunzip > file | ansible.builtin.get_url | Downloads and extracts file |
| chmod +x | ansible.builtin.file | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None
**System packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but Chef Automate has its own dependencies

## Checks for the Migration

**Files to verify**: 
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system requirements
ansible.builtin.command:
  cmd: free -m
  register: memory_result

ansible.builtin.command:
  cmd: df -h
  register: disk_result

# Verify network connectivity
ansible.builtin.uri:
  url: https://packages.chef.io
  status_code: 200

# Check if Chef is already installed
ansible.builtin.stat:
  path: /hab/sup/default/data/services.dat
  register: chef_installed
```

## Ansible Playbook Example

Here's a sample Ansible playbook structure for the Chef Automate deployment:

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
        creates: /hab/sup/default/data/services.dat
    
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

Note: The scripts provided are Bash scripts, not PowerShell scripts. The migration plan above converts these Bash scripts to Ansible, which is still relevant for your automation needs. If you specifically need PowerShell to Ansible migration, please provide the PowerShell scripts for analysis.