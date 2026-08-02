---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys the Chef Automate and Infra Server products, and configures a user and organization. The script is actually a Bash script, not PowerShell, so we'll be migrating from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set hostname for the server
- Configure kernel parameters for Chef Automate
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create a Chef user
- Create a Chef organization and associate the user

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
```

**Modules:**
None

**DSC Configurations:**
None

**Data Files:**
None

## Module Explanation

The script performs operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for Chef Automate configuration (hostname, username, organization, etc.)
   - Sets the system hostname using `hostnamectl`
   - Configures kernel parameters using `sysctl`
   - Downloads and extracts the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a Chef user
   - Creates a Chef organization and associates the user
   - Ansible equivalent: Custom Ansible playbook with system configuration and Chef Automate deployment tasks

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Configures kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (script is Bash)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but Chef Automate has its own dependencies

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- User PEM file (created as ${username}.pem)
- Organization validator PEM file (created as ${orgname}-validator.pem)

**Registry keys**: None (Linux-based deployment)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

**Firewall rules**: None explicitly configured in the script

## Pre-flight checks:
```
# Check system requirements
- Verify VM has sufficient resources (CPU, RAM, disk space)
- Verify network connectivity
- Verify hostname resolution
- Check kernel parameters after setting:
  sysctl vm.max_map_count
  sysctl vm.dirty_expire_centisecs
- Verify Chef Automate UI is accessible
- Verify Chef Infra Server API is accessible
- Verify user can authenticate with generated PEM file
```

## Ansible Playbook Implementation

Here's a detailed guide for implementing this as an Ansible playbook:

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
    automate_cli_url: "https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip"
    
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
        url: "{{ automate_cli_url }}"
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
        cmd: /tmp/chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
        creates: /etc/chef-automate/config.toml
        
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

**Implementation Notes:**
1. Store sensitive variables like passwords in Ansible Vault
2. Consider using `wait_for` module to ensure Chef services are up before proceeding
3. Add error handling and idempotence checks
4. Consider breaking this into roles for better organization
5. Add tags for selective execution of tasks
6. Add handlers to restart services if needed

This playbook follows the same workflow as the original Bash script but leverages Ansible's idempotent modules where possible. For the Chef Automate CLI deployment and Chef server commands, we use the command module with the `creates` parameter to ensure idempotence.