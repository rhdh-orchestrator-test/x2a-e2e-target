---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I need to clarify something important: The files provided are Bash shell scripts (.sh), not PowerShell (.ps1) scripts. The analysis summary shows 0 PowerShell files analyzed, which is consistent with what I found. 

Let me prepare a migration plan for converting these Bash scripts to Ansible, rather than PowerShell to Ansible as initially requested:

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download and install Chef Automate CLI, deploy Chef products, and configure users and organizations. The scripts are Bash shell scripts, not PowerShell.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and/or Chef Infra Server
- Create Chef user
- Create Chef organization
- Associate user with organization

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
   - Sets variables for Chef configuration (hostname, username, organization details)
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets the same variables and performs the same system configurations
   - Deploys only the Chef Infra Server product
   - Creates the same user and organization
   - Ansible equivalent: Same modules as above with different parameters

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract Chef Automate CLI |
| chmod +x | ansible.builtin.file | Set executable permissions |
| chef-automate deploy | ansible.builtin.command | Run Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**Module dependencies**: None
**System packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but Chef Automate has its own dependencies

## Checks for the Migration

**Files to verify**: 
- /path/to/chef-automate (CLI tool)
- /path/to/[username].pem (user key file)
- /path/to/[orgname]-validator.pem (organization validator key)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```
# Check system requirements
ansible.builtin.command: cmd="grep -c processor /proc/cpuinfo"
ansible.builtin.command: cmd="free -m | grep Mem | awk '{print $2}'"
ansible.builtin.command: cmd="df -h / | grep / | awk '{print $4}'"

# Check network connectivity
ansible.builtin.uri: url="https://packages.chef.io" status_code=200

# Verify hostname resolution
ansible.builtin.command: cmd="getent hosts {{ hostname }}"
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace the deploy-automate.sh script:

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
    
  tasks:
    - name: Set hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
      
    - name: Set vm.max_map_count
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        reload: yes
        
    - name: Set vm.dirty_expire_centisecs
      ansible.posix.sysctl:
        name: vm.dirty_expire_centisecs
        value: '20000'
        state: present
        reload: yes
        
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate.gz
        
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate.gz > /tmp/chef-automate
      args:
        creates: /tmp/chef-automate
        
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
        creates: /hab
        
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: The scripts provided are Bash shell scripts (.sh), not PowerShell (.ps1) scripts. This migration plan converts Bash shell scripts to Ansible, not PowerShell to Ansible as initially requested.