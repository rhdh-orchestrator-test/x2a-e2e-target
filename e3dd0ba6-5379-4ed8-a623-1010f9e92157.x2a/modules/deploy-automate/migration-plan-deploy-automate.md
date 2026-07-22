---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate and Chef Infra Server Deployment

**TLDR**: The scripts are actually Bash scripts (not PowerShell) that deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download Chef Automate CLI, deploy the products, and create initial user and organization configurations.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and/or Chef Infra Server
- Create initial user account
- Create initial organization

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None (no PowerShell modules)

**DSC Configurations:**
None (no PowerShell DSC configurations)

**Data Files:**
None (no PowerShell data files)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and prepares Chef Automate CLI
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Server performance
   - Downloads and prepares Chef Automate CLI
   - Deploys only Chef Infra Server product
   - Creates initial admin user with specified credentials
   - Creates initial organization and associates the admin user
   - Ansible equivalent: Same modules as above with different parameters

## PowerShell to Ansible Mapping

Note: Since these are Bash scripts, not PowerShell, I'll map the Bash commands to Ansible modules:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl \| gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (these are Bash scripts)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None specified in scripts

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key)

**Registry keys**: None (Linux system)
**Services to check**: 
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check Chef Automate status (after deployment)
sudo ./chef-automate status

# Verify user creation
sudo chef-server-ctl user-list

# Verify organization creation
sudo chef-server-ctl org-list
```

## Ansible Playbook Structure

Here's how you would structure an Ansible playbook to replace these Bash scripts:

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
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        state: present
        sysctl_set: yes
      loop:
        - { key: "vm.max_map_count", value: "262144" }
        - { key: "vm.dirty_expire_centisecs", value: "20000" }

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
        chdir: /root

    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /root/chef-automate
        mode: '0755'

    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: >
          ./chef-automate deploy 
          {% if deploy_automate %}--product automate {% endif %}
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        chdir: /root
        creates: /etc/chef-automate/config.toml

    - name: Create Chef user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} 
          "{{ userpassword }}" --filename {{ userfilename }}
      args:
        chdir: /root
        creates: "/root/{{ userfilename }}"

    - name: Create Chef organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" 
          --association_user {{ username }} --filename {{ orgfilename }}
      args:
        chdir: /root
        creates: "/root/{{ orgfilename }}"
```

Note: Since these are Bash scripts and not PowerShell scripts as initially assumed, I've provided an Ansible migration plan that converts the Bash commands to equivalent Ansible modules and tasks.