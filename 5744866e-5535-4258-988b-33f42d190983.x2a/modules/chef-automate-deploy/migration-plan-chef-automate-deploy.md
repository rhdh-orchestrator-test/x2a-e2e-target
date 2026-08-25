---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: The scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download the Chef Automate CLI, deploy the Chef products, and configure initial users and organizations. These are Bash scripts, not PowerShell, so the migration will be from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server
- Creating initial Chef user
- Creating initial Chef organization

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
   - Sets variables for Chef configuration (hostname, username, organization, etc.)
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and extracts the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with acceptance of terms
   - Creates an initial user in Chef Infra Server
   - Creates an initial organization in Chef Infra Server
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for Chef configuration
   - Sets the system hostname
   - Configures kernel parameters
   - Downloads and extracts the Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates an initial user and organization
   - Ansible equivalent: Same modules as above with different parameters

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl \| gunzip > file | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract in two steps |
| chmod +x | ansible.builtin.file | Set executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Run Chef Automate CLI with parameters |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (these are Bash scripts)
**Linux packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated

## Checks for the Migration

**Files to verify**:
- /etc/hostname
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
# Check hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check Chef Automate status
sudo ./chef-automate status

# Verify Chef Infra Server is running
sudo chef-server-ctl status
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
        mode: '0644'

    - name: Extract Chef Automate CLI
      ansible.builtin.command:
        cmd: gunzip -c /tmp/chef-automate_linux_amd64.zip > chef-automate
        creates: chef-automate
      args:
        chdir: "{{ ansible_env.HOME }}"

    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: "{{ ansible_env.HOME }}/chef-automate"
        mode: '0755'

    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: >
          ./chef-automate deploy 
          {% if deploy_automate %}--product automate {% endif %}
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        chdir: "{{ ansible_env.HOME }}"
        creates: /hab

    - name: Create Chef user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create 
          {{ username }} 
          {{ longusername | quote }} 
          {{ useremail }} 
          {{ userpassword | quote }} 
          --filename {{ userfilename }}
      args:
        creates: "{{ ansible_env.HOME }}/{{ userfilename }}"

    - name: Create Chef organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create 
          {{ orgname }} 
          {{ longorgname | quote }} 
          --association_user {{ username }} 
          --filename {{ orgfilename }}
      args:
        creates: "{{ ansible_env.HOME }}/{{ orgfilename }}"
```

Note: This migration plan is for Bash scripts, not PowerShell as initially requested. The scripts provided are Linux Bash scripts for deploying Chef Automate and Chef Infra Server.