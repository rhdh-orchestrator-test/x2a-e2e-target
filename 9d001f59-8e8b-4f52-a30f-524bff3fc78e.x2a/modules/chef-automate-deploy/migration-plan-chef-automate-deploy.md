---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I don't see any PowerShell files in the repository. The file you've asked me to analyze (setup-automate/deploy-automate.sh) is actually a Bash script for deploying Chef Automate and Chef Infra Server, not a PowerShell script. 

Let me provide a migration plan for converting this Bash script to Ansible:

# Migration Plan: Chef Automate Deployment Script

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads and installs Chef Automate CLI, deploys Chef products, and creates a user and organization in Chef Server.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set hostname for the server
- Configure kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create a Chef user
- Create a Chef organization and associate the user with it

## File Structure

**Scripts:**
setup-automate/deploy-automate.sh

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for Chef Automate and Chef Infra Server configuration
   - Sets the hostname of the system
   - Configures kernel parameters for optimal performance
   - Downloads and installs Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

## PowerShell to Ansible Mapping

Since this is a Bash script, not PowerShell, I'll map the Bash commands to Ansible modules:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl \| gunzip > file | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts files |
| chmod +x | ansible.builtin.file | Sets file permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate CLI |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but Chef Automate likely has its own dependencies

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
# Check if Chef Automate is running
curl -k https://localhost/api/v0/health
# Check if Chef Infra Server is running
knife user list -s https://localhost/organizations/orgname -k /path/to/user.pem
```

## Ansible Playbook Example

Here's how you might implement this in Ansible:

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
        mode: '0644'

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

Note: This playbook assumes you're running it from the same directory where you want the Chef Automate CLI to be installed. You might want to adjust paths according to your needs.