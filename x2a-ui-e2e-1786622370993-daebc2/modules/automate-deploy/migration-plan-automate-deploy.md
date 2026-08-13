---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Script

**TLDR**: This is a Bash script (not PowerShell) that deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys Chef Automate and Infra Server products, and creates a user and organization in Chef Server.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management)

**Key Operations**:
- Sets hostname for the server
- Configures system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloads and installs Chef Automate CLI
- Deploys Chef Automate and Chef Infra Server products
- Creates a user in Chef Server
- Creates an organization in Chef Server and associates the user

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Note**: The script being analyzed is a Bash script, not PowerShell. There are no PowerShell (.ps1) files in the provided directories.

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for configuration (hostname, username, organization name, etc.)
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys Chef Automate and Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url | Downloads Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef Server user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef Server organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated in the script

## Checks for the Migration

**Files to verify**: 
- Chef Automate CLI executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```
# Check system requirements
- Verify VM has sufficient resources (CPU, RAM, disk space)
- Verify network connectivity
- Verify hostname resolution
- Check if ports required by Chef Automate and Chef Infra Server are available

# Post-deployment verification
- Verify Chef Automate UI is accessible
- Verify Chef Infra Server is operational
- Verify user creation was successful
- Verify organization creation was successful
```

## Ansible Playbook Example

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
    
    - name: Move Chef Automate CLI to current directory
      ansible.builtin.copy:
        src: /tmp/chef-automate
        dest: ./chef-automate
        mode: '0755'
        remote_src: yes
    
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        creates: /hab
    
    - name: Create Chef Server user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
    
    - name: Create Chef Server organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```