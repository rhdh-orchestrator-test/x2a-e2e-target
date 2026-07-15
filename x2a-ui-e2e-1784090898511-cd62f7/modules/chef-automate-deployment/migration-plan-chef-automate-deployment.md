---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys Chef Automate and Infra Server products, and configures a user and organization. The script is actually a Bash script, not PowerShell, so we'll be migrating from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create a Chef user
- Create a Chef organization and associate the user with it

## File Structure

**Scripts:**
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh

**Modules:**
None

**DSC Configurations:**
None

**Data Files:**
None

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for configuration (hostname, username, organization name, etc.)
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and extracts the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl \| gunzip > file | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract file |
| chmod +x | ansible.builtin.file | Set file permissions |
| ./chef-automate deploy | ansible.builtin.command | Run Chef Automate CLI command |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**Module dependencies**: None
**System packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but likely requires sufficient system resources

## Checks for the Migration

**Files to verify**: 
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```
# Check system resources
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_count"

# Check if Chef Automate is already installed
ansible all -m stat -a "path=/usr/bin/chef-automate"

# Check if required ports are available (80, 443)
ansible all -m shell -a "netstat -tuln | grep -E ':80|:443'"
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace the Bash script:

```yaml
---
- name: Deploy Chef Automate and Chef Infra Server
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
        remote_src: yes
        mode: '0755'
    
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        creates: /hab
    
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

Note: This playbook includes idempotence checks using the `creates` parameter to prevent re-running commands if the expected files or directories already exist. For production use, you should store sensitive information like passwords in Ansible Vault.