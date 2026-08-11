---
source-path: setup-automate/deploy-automate.sh
---

Now I'll create a migration plan based on the files I've examined:

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers the deployment of Chef Automate and Chef Infra Server from Bash scripts to Ansible. The scripts set system parameters, download Chef Automate CLI, deploy Chef Automate and/or Chef Infra Server, and configure initial users and organizations.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating initial user and organization in Chef Server

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets the hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and extracts Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for hostname, user details, and organization details
   - Sets the hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads and extracts Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates the user
   - Ansible equivalent: Same modules as above but with different parameters for deployment

## PowerShell to Ansible Mapping

Note: These are actually Bash scripts, not PowerShell, but here's the mapping to Ansible:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract Chef Automate CLI |
| chmod +x | ansible.builtin.file | Set executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploy Chef Automate/Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef Server user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef Server organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

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

# Check if Chef Server is already installed
ansible all -m command -a "chef-server-ctl status" --ignore-errors
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
      ansible.builtin.command:
        cmd: gunzip -c /tmp/chef-automate_linux_amd64.zip > /tmp/chef-automate
        creates: /tmp/chef-automate
        
    - name: Set executable permissions on Chef Automate CLI
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: >
          /tmp/chef-automate deploy 
          {% if deploy_automate %}--product automate {% endif %}
          --product infra-server 
          --accept-terms-and-mlsa=true
        creates: /usr/bin/chef-automate
      when: deploy_automate
        
    - name: Deploy only Chef Infra Server
      ansible.builtin.command:
        cmd: >
          /tmp/chef-automate deploy 
          --product infra-server 
          --accept-terms-and-mlsa=true
        creates: /usr/bin/chef-automate
      when: not deploy_automate
        
    - name: Create Chef Server user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create 
          {{ username }} 
          {{ longusername }} 
          {{ useremail }} 
          "{{ userpassword }}" 
          --filename {{ userfilename }}
        creates: "{{ userfilename }}"
        
    - name: Create Chef Server organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create 
          {{ orgname }} 
          "{{ longorgname }}" 
          --association_user {{ username }} 
          --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: For production use, you should consider using Ansible Vault to secure sensitive variables like passwords.