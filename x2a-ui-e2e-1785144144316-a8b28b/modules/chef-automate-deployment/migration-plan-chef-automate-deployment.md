---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Script

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads Chef Automate CLI, deploys the products, and creates a user and organization. The script is actually a Bash script, not PowerShell, so we'll be migrating from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set hostname for the server
- Configure system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create a Chef user
- Create a Chef organization and associate the user with it

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
```

**Modules:**
None

**DSC Configurations:**
None

**Data Files:**
None

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets the hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

## PowerShell to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Chef Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates a Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates a Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (this is a Bash script)
**Windows Features**: None (this is for Linux)
**External packages**: curl, gunzip
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Registry keys**: None (Linux doesn't use registry)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: 
- Port 443 (HTTPS) should be open for Chef Automate web UI
- Port 9631 (Habitat Supervisor) should be open

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb"
ansible all -m setup -a "filter=ansible_processor_vcpus"
ansible all -m setup -a "filter=ansible_distribution*"

# Check network connectivity
ansible all -m uri -a "url=https://packages.chef.io timeout=5"

# Check disk space
ansible all -m shell -a "df -h / | awk 'NR==2 {print $4}'"
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
        dest: /tmp/chef-automate_linux_amd64.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate_linux_amd64.zip > chef-automate
      args:
        creates: chef-automate
        
    - name: Set execute permissions on Chef Automate CLI
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        creates: /hab
        
    - name: Create Chef user
      ansible.builtin.command: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```

Note: This playbook includes idempotence checks using the `creates` parameter to ensure tasks are not re-run unnecessarily. For production use, you should use Ansible Vault to secure sensitive information like passwords.