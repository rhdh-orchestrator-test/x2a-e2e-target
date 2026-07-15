---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys Chef Automate and Infra Server products, and creates a user and organization in Chef Server. The script is currently implemented in Bash, not PowerShell, and needs to be migrated to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server products
- Creating a user in Chef Server
- Creating an organization in Chef Server and associating it with the user

## File Structure

**Scripts:**
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh

**Modules:**
None found

**DSC Configurations:**
None found

**Data Files:**
None found

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for configuration (hostname, username, organization name, etc.)
   - Sets the hostname of the system
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and prepares the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates it with the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

## PowerShell to Ansible Mapping

Note: The original script is in Bash, not PowerShell. Here's the mapping to Ansible:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.shell | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates a user in Chef Server |
| chef-server-ctl org-create | ansible.builtin.command | Creates an organization in Chef Server |

## Dependencies

**PowerShell Module dependencies**: None (original is Bash)
**Windows Features**: None (runs on Linux)
**External packages**: Chef Automate CLI
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Registry keys**: None (Linux system)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: 
- Port 443 (HTTPS) should be open for Chef Automate UI
- Port 9631 (Chef Habitat) should be open

## Pre-flight checks:
```
# Check if Chef Automate is running
curl -k https://localhost/api/v0/health

# Check if Chef Infra Server is running
chef-server-ctl status

# Verify user creation
chef-server-ctl user-list | grep <username>

# Verify organization creation
chef-server-ctl org-list | grep <orgname>
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
        dest: /tmp/chef-automate.gz
    
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate.gz > chef-automate
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
    
    - name: Create user in Chef Server
      ansible.builtin.command: >
        chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
    
    - name: Create organization in Chef Server
      ansible.builtin.command: >
        chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```

Note: The original script provided is a Bash script, not PowerShell. The migration plan above shows how to convert this Bash script to Ansible. If there is a specific PowerShell module named 'chef-automate-deployment' that needs to be analyzed, it was not found in the provided files.