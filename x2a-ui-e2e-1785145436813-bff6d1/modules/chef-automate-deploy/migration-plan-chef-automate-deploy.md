---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Script

**TLDR**: This is a Bash script (not PowerShell) that deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads Chef Automate CLI, deploys Chef products, and creates a user and organization in Chef Server.

## Service Type and Configuration

**Service Type**: Configuration Management System (Chef Automate and Chef Infra Server)

**Key Operations**:
- Sets hostname for the server
- Configures system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloads and installs Chef Automate CLI
- Deploys Chef Automate and Chef Infra Server products
- Creates a Chef user with specified credentials
- Creates a Chef organization and associates the user with it

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Note**: The analysis requested PowerShell code migration, but the provided script is a Bash script, not PowerShell. There are no PowerShell (.ps1) files or modules in the provided directory structure.

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for Chef Automate and Chef Server configuration
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI and makes it executable
   - Deploys Chef Automate and Chef Infra Server products
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Configures kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: Chef Automate, Chef Infra Server

## Ansible Playbook Structure

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
    userpassword: 'password'  # Consider using Ansible Vault for passwords
    orgname: 'lab'
    longorgname: 'Chef Lab'
    userfilename: "{{ username }}.pem"
    orgfilename: "{{ orgname }}-validator.pem"
    
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
        dest: /tmp/chef-automate.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.unarchive:
        src: /tmp/chef-automate.zip
        dest: /tmp/
        remote_src: yes
        
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
        chdir: /tmp
      register: deploy_result
      changed_when: deploy_result.rc == 0
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
      register: user_create_result
      changed_when: user_create_result.rc == 0
      
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
      register: org_create_result
      changed_when: org_create_result.rc == 0
```

## Checks for the Migration

**Files to verify**: 
- /tmp/chef-automate
- {{ userfilename }} (e.g., jtonello.pem)
- {{ orgfilename }} (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
```yaml
- name: Check if Chef Automate is accessible
  ansible.builtin.uri:
    url: https://{{ hostname }}
    validate_certs: no
  register: chef_automate_check
  ignore_errors: yes

- name: Display Chef Automate status
  ansible.builtin.debug:
    msg: "Chef Automate is {{ 'accessible' if chef_automate_check.status == 200 else 'not accessible' }}"
```

## Important Notes

1. The original script is a Bash script, not PowerShell as requested in the analysis. The migration plan converts this Bash script to Ansible.

2. Security considerations:
   - The script contains hardcoded passwords which should be stored securely using Ansible Vault in production
   - Consider using HTTPS validation in production environments

3. Idempotency:
   - The Ansible playbook includes checks to ensure tasks are idempotent where possible
   - For command-based tasks, the `creates` parameter is used to prevent re-running commands

4. The Chef Automate deployment might take significant time to complete. Consider adding appropriate timeouts and async task handling for production use.