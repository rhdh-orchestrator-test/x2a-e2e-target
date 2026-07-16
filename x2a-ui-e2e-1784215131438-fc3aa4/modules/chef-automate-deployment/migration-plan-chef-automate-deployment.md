---
source-path: setup-automate/deploy-automate.sh
---

Now I'll create a migration plan based on the files I've examined:

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys the Chef products, and configures a user and organization. The migration will convert these bash scripts to Ansible playbooks that perform the same operations.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create Chef user and organization
- Generate and save authentication keys

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

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI and makes it executable
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates a Chef user with specified details
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets the same variables and performs the same system configurations
   - Deploys only the Chef Infra Server product
   - Creates the same user and organization
   - Ansible equivalent: Same modules as above but with different parameters for the deployment command

## PowerShell to Ansible Mapping

Note: These are actually Bash scripts, not PowerShell, so I'm mapping Bash commands to Ansible modules:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef products |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (these are Bash scripts)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**Registry keys**: None (Linux-based deployment)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: None explicitly configured in the scripts

## Pre-flight checks:
```
# Check system hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check if Chef Automate CLI is installed
ls -la chef-automate

# Check if Chef Automate and Chef Infra Server are running
sudo chef-automate status

# Check if user and organization exist
sudo chef-server-ctl user-list
sudo chef-server-ctl org-list

# Check if key files exist
ls -la ${username}.pem
ls -la ${orgname}-validator.pem
```

## Ansible Playbook Structure

Here's a suggested structure for the Ansible playbook:

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
    - name: Set system hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"

    - name: Set vm.max_map_count kernel parameter
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        sysctl_set: yes

    - name: Set vm.dirty_expire_centisecs kernel parameter
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
      ansible.builtin.shell: gunzip -c /tmp/chef-automate.zip > chef-automate
      args:
        creates: chef-automate

    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'

    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command: >
        ./chef-automate deploy 
        {% if deploy_automate %}--product automate {% endif %}
        --product infra-server 
        --accept-terms-and-mlsa=true
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

This playbook includes all the operations from the original bash scripts and provides a variable to control whether to deploy Chef Automate along with Chef Infra Server or just Chef Infra Server alone.