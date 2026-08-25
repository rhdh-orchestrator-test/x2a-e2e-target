---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: The scripts deploy Chef Automate and Chef Infra Server on Linux systems. They are actually Bash scripts, not PowerShell scripts. The scripts set system parameters, download Chef Automate CLI, deploy Chef products, and create initial users and organizations.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters for optimal performance
- Download and install Chef Automate CLI
- Deploy Chef Automate and/or Chef Infra Server
- Create initial admin user
- Create initial organization
- Generate and save authentication keys

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None (no PowerShell modules found)

**DSC Configurations:**
None (no DSC configurations found)

**Data Files:**
None (no separate data files found)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for Chef Automate performance
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates initial admin user
   - Creates initial organization
   - Ansible equivalent: Use ansible.builtin.template for configuration and ansible.builtin.command for Chef operations

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for hostname, user details, and organization details
   - Sets system hostname using hostnamectl
   - Configures kernel parameters for Chef Server performance
   - Downloads Chef Automate CLI
   - Deploys only Chef Infra Server
   - Creates initial admin user
   - Creates initial organization
   - Ansible equivalent: Use ansible.builtin.template for configuration and ansible.builtin.command for Chef operations

## PowerShell to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Configure kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Set executable permissions |
| chef-automate deploy | ansible.builtin.command | Run Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**Module dependencies**: None (these are Bash scripts, not PowerShell)
**System requirements**: Linux system with sufficient resources for Chef Automate
**External packages**: curl, gunzip
**Service dependencies**: None explicitly defined in scripts

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**:
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system resources
ansible.builtin.command: free -m
ansible.builtin.command: df -h

# Check network connectivity
ansible.builtin.uri:
  url: https://packages.chef.io
  status_code: 200

# Verify hostname resolution
ansible.builtin.command: getent hosts {{ hostname }}
```

## Ansible Playbook Structure

Since the original scripts are Bash and not PowerShell, here's how you would structure the Ansible playbook:

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
        creates: /hab
      when: deploy_automate
        
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: >
          /tmp/chef-automate deploy 
          --product infra-server 
          --accept-terms-and-mlsa=true
        creates: /hab
      when: not deploy_automate
        
    - name: Create Chef user
      ansible.builtin.command:
        cmd: >
          chef-server-ctl user-create 
          {{ username }} {{ longusername }} {{ useremail }} 
          "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: >
          chef-server-ctl org-create 
          {{ orgname }} "{{ longorgname }}" 
          --association_user {{ username }} 
          --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: The original scripts are Bash scripts, not PowerShell scripts. The migration plan has been adapted to show how to convert these Bash scripts to Ansible playbooks.