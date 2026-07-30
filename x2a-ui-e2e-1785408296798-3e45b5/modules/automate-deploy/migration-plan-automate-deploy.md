---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate and Chef Infra Server Deployment

**TLDR**: The scripts provided are actually Bash scripts (not PowerShell) that deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management)

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating initial user accounts
- Creating initial organizations
- Associating users with organizations

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None (no PowerShell modules found)

**DSC Configurations:**
None (no PowerShell DSC configurations found)

**Data Files:**
None (no PowerShell data files found)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets hostname for the server
   - Configures system parameters for optimal Chef Automate performance
   - Downloads and installs Chef Automate CLI
   - Deploys both Chef Automate and Chef Infra Server
   - Creates an initial user account
   - Creates an initial organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets hostname for the server
   - Configures system parameters
   - Downloads and installs Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates an initial user account
   - Creates an initial organization and associates the user with it
   - Ansible equivalent: Same modules as above with different parameters

## PowerShell to Ansible Mapping

Note: Since the provided scripts are Bash scripts (not PowerShell), I'll provide the Bash to Ansible mapping instead:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters at runtime |
| curl + gunzip | ansible.builtin.get_url | Downloads files from HTTP/HTTPS |
| chmod | ansible.builtin.file | Sets file permissions |
| chef-automate deploy | ansible.builtin.command | Runs the Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**Module dependencies**: None (no PowerShell modules)
**System requirements**: Linux system with sufficient resources for Chef Automate and Chef Infra Server
**External packages**: Chef Automate CLI (downloaded during script execution)
**Service dependencies**: None explicitly defined in scripts

## Checks for the Migration

**Files to verify**:
- /etc/hostname (modified by hostnamectl)
- chef-automate executable (downloaded and made executable)
- User PEM file (created during user creation)
- Organization validator PEM file (created during org creation)

**Services to check**:
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system resources
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_*"

# Check hostname resolution
ansible all -m command -a "getent hosts {{ hostname }}"

# Check kernel parameters
ansible all -m command -a "sysctl vm.max_map_count vm.dirty_expire_centisecs"

# Check connectivity to Chef package repository
ansible all -m uri -a "url=https://packages.chef.io/files/current/latest/chef-automate-cli/ status_code=200"
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace these Bash scripts:

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
    - name: Set hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
      
    - name: Set kernel parameters
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
        dest: /tmp/chef-automate_linux_amd64.zip
        mode: '0644'
      
    - name: Extract Chef Automate CLI
      ansible.builtin.command:
        cmd: gunzip -c /tmp/chef-automate_linux_amd64.zip > chef-automate
        creates: chef-automate
      args:
        chdir: /tmp
      
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'
      
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: >
          ./chef-automate deploy 
          {% if deploy_automate %}--product automate {% endif %}
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        chdir: /tmp
        creates: /hab
      when: deploy_automate
      
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: >
          ./chef-automate deploy 
          --product infra-server 
          --accept-terms-and-mlsa=true
      args:
        chdir: /tmp
        creates: /hab
      when: not deploy_automate
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create 
          {{ username }} {{ longusername }} {{ useremail }} 
          "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
      
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create 
          {{ orgname }} "{{ longorgname }}" 
          --association_user {{ username }} 
          --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
```

Note: The scripts provided are Bash scripts, not PowerShell scripts. The migration plan has been adjusted accordingly to convert these Bash scripts to Ansible playbooks.