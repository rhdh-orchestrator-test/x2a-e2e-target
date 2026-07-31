---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers the conversion of a Bash script for deploying Chef Automate and Chef Infra Server to Ansible. The script sets system parameters, downloads Chef Automate CLI, deploys Chef Automate and Infra Server, and configures a user and organization.

## Service Type and Configuration

**Service Type**: Configuration Management System (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting hostname for the server
- Configuring kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server
- Creating a Chef user
- Creating a Chef organization and associating the user

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
```

**Note**: The analysis did not reveal any PowerShell scripts. The file provided is a Bash script, not PowerShell. The migration will convert this Bash script to Ansible.

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets the hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user
   - Ansible equivalent: Multiple Ansible modules including `hostname`, `sysctl`, `get_url`, `command`, etc.

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Configures kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Chef Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates a Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates a Chef organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated in the script

## Checks for the Migration

**Files to verify**: 
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Ansible Playbook Structure

Here's a detailed Ansible playbook structure to replace the Bash script:

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
        dest: /tmp/chef-automate_linux_amd64.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.unarchive:
        src: /tmp/chef-automate_linux_amd64.zip
        dest: /tmp/
        remote_src: yes
        
    - name: Move Chef Automate CLI to working directory
      ansible.builtin.copy:
        src: /tmp/chef-automate
        dest: ./chef-automate
        remote_src: yes
        mode: '0755'
        
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        creates: /hab
      register: deploy_result
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        creates: "{{ userfilename }}"
      register: user_create_result
      
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        creates: "{{ orgfilename }}"
      register: org_create_result
```

## Pre-flight checks:

```yaml
---
- name: Chef Automate Pre-flight Checks
  hosts: chef_servers
  become: yes
  tasks:
    - name: Check system memory
      ansible.builtin.command:
        cmd: free -m
      register: memory_check
      changed_when: false
      
    - name: Check disk space
      ansible.builtin.command:
        cmd: df -h
      register: disk_check
      changed_when: false
      
    - name: Check CPU resources
      ansible.builtin.command:
        cmd: lscpu
      register: cpu_check
      changed_when: false
      
    - name: Check current kernel parameters
      ansible.builtin.command:
        cmd: sysctl vm.max_map_count vm.dirty_expire_centisecs
      register: sysctl_check
      changed_when: false
      
    - name: Display system information
      ansible.builtin.debug:
        msg: 
          - "Memory Information: {{ memory_check.stdout_lines }}"
          - "Disk Information: {{ disk_check.stdout_lines }}"
          - "CPU Information: {{ cpu_check.stdout_lines }}"
          - "Kernel Parameters: {{ sysctl_check.stdout_lines }}"
          
    - name: Verify Chef Automate services after installation
      ansible.builtin.command:
        cmd: chef-automate status
      register: automate_status
      changed_when: false
      ignore_errors: yes
      
    - name: Display Chef Automate status
      ansible.builtin.debug:
        msg: "Chef Automate Status: {{ automate_status.stdout_lines }}"
```

## Additional Notes for Migration

1. **Variable Security**: In Ansible, consider using `ansible-vault` to encrypt sensitive variables like passwords.

2. **Idempotency**: The Ansible playbook uses `creates` arguments to ensure idempotency for commands that should only run once.

3. **Error Handling**: Consider adding more robust error handling and conditional tasks based on the results of previous tasks.

4. **Templating**: For more complex deployments, consider using Ansible templates for configuration files.

5. **Inventory Management**: Create appropriate inventory files to target the correct servers.

6. **Role Structure**: For production use, consider organizing the playbook into an Ansible role with appropriate directory structure.

7. **Testing**: Implement testing using Ansible's `--check` mode and molecule for more comprehensive testing.