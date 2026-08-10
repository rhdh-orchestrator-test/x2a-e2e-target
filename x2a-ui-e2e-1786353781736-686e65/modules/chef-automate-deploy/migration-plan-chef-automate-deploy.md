---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This migration plan covers the conversion of a Bash script for deploying Chef Automate and Chef Infra Server to Ansible. The script sets system parameters, downloads Chef Automate CLI, deploys Chef Automate and Infra Server, and configures a user and organization.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
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
   - Sets variables for Chef Automate configuration (hostname, username, organization details)
   - Sets the hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user
   - Ansible equivalent: Multiple Ansible modules will be used to replicate this functionality

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Configures kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

## Pre-flight checks:
- Verify system meets Chef Automate requirements
- Check network connectivity to packages.chef.io
- Ensure sufficient disk space for installation
- Verify system has required memory (at least 4GB RAM recommended)

## Ansible Playbook Implementation

Here's a detailed guide for implementing the equivalent functionality in Ansible:

```yaml
---
# playbook.yml - Deploy Chef Automate and Chef Infra Server

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
    chef_automate_cli_url: "https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip"
    
  tasks:
    - name: Set hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
      
    - name: Configure vm.max_map_count
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        sysctl_set: yes
        
    - name: Configure vm.dirty_expire_centisecs
      ansible.posix.sysctl:
        name: vm.dirty_expire_centisecs
        value: '20000'
        state: present
        sysctl_set: yes
        
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: "{{ chef_automate_cli_url }}"
        dest: /tmp/chef-automate.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.unarchive:
        src: /tmp/chef-automate.zip
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
      
    - name: Display deployment output
      ansible.builtin.debug:
        var: deploy_result.stdout_lines
      when: deploy_result.stdout_lines is defined
        
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

### Implementation Notes:

1. **Variable Management**:
   - Store sensitive variables like passwords in Ansible Vault
   - Consider using host_vars or group_vars for environment-specific configurations

2. **Idempotence**:
   - The playbook uses `creates` arguments to ensure commands don't run repeatedly
   - System settings are applied using proper Ansible modules that handle idempotence

3. **Error Handling**:
   - Add error handling with `failed_when` conditions for critical tasks
   - Consider adding `ignore_errors` for non-critical tasks

4. **Security Considerations**:
   - PEM files contain sensitive information; ensure proper permissions
   - Consider using `no_log: true` for tasks that display sensitive information

5. **Verification**:
   - Add verification tasks to check if Chef Automate and Chef Infra Server are running correctly
   - Consider adding a handler to notify administrators of deployment status

This playbook provides a direct translation of the bash script functionality to Ansible, maintaining the same workflow while leveraging Ansible's idempotence and declarative approach.