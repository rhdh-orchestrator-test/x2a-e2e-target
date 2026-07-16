---
source-path: setup-automate/deploy-automate.sh
---

Now I'll create a migration plan based on the files I've examined:

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers the conversion of Bash scripts for deploying Chef Automate and Chef Infra Server to Ansible playbooks. The scripts configure system settings, download and install Chef Automate CLI, deploy Chef Automate and/or Chef Infra Server, and create initial user and organization configurations.

## Service Type and Configuration

**Service Type**: Configuration Management System (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
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

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with license acceptance
   - Creates initial Chef user with specified credentials
   - Creates initial Chef organization and associates it with the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for hostname, user details, and organization details
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Server performance
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server with license acceptance
   - Creates initial Chef user with specified credentials
   - Creates initial Chef organization and associates it with the user
   - Ansible equivalent: Same modules as above but with different parameters for the deploy command

## PowerShell to Ansible Mapping

Note: These are actually Bash scripts, not PowerShell, but here's the mapping to Ansible:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract Chef Automate CLI |
| chmod +x | ansible.builtin.file | Set executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Run Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined in scripts

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Kernel parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

**Services to check**:
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_cores"

# Check if Chef Automate is already installed
ansible all -m stat -a "path=/usr/bin/chef-automate"

# Check if Chef Server is already installed
ansible all -m command -a "chef-server-ctl status" --ignore-errors
```

## Ansible Playbook Example

Here's a sample Ansible playbook structure for the Chef Automate deployment:

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
    deploy_automate: true  # Set to false to deploy only Chef Infra Server

  tasks:
    - name: Set system hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"

    - name: Configure kernel parameters for Chef Automate
      ansible.posix.sysctl:
        name: "{{ item.name }}"
        value: "{{ item.value }}"
        state: present
        reload: yes
      loop:
        - { name: 'vm.max_map_count', value: '262144' }
        - { name: 'vm.dirty_expire_centisecs', value: '20000' }

    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate.gz
        mode: '0644'

    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate.gz > /tmp/chef-automate
      args:
        creates: /tmp/chef-automate

    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'

    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      when: deploy_automate | bool
      args:
        creates: /usr/bin/chef-automate

    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product infra-server --accept-terms-and-mlsa=true
      when: not deploy_automate | bool
      args:
        creates: /usr/bin/chef-automate

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