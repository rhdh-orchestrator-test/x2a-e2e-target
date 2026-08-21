---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: The scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download the Chef Automate CLI, deploy the Chef products, and configure users and organizations. These are bash scripts, not PowerShell, so the migration will be from bash to Ansible rather than from PowerShell to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting hostname for the server
- Configuring system parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating Chef user accounts
- Creating Chef organizations
- Associating users with organizations

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
None found

**DSC Configurations:**
None found

**Data Files:**
None found (configuration is embedded in the scripts)

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and prepares the Chef Automate CLI
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Server performance
   - Downloads and prepares the Chef Automate CLI
   - Deploys only the Chef Infra Server product
   - Creates a Chef user with specified credentials
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Same modules as above but with different parameters for the deployment command

## Bash to Ansible Mapping

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

**Module dependencies**: None
**System packages**: curl, gunzip
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but likely requires networking and sufficient system resources

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- ${username}.pem (user key file)
- ${orgname}-validator.pem (organization validator key file)

**System parameters**:
- vm.max_map_count=262144
- vm.dirty_expire_centisecs=20000

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

# Check kernel parameters
ansible.posix.sysctl:
  name: vm.max_map_count
  
ansible.posix.sysctl:
  name: vm.dirty_expire_centisecs
```

## Example Ansible Playbook

Here's a starting point for the Ansible playbook that would replace these bash scripts:

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
        
    - name: Extract Chef Automate CLI
      ansible.builtin.command:
        cmd: gunzip -c /tmp/chef-automate_linux_amd64.zip > chef-automate
        creates: chef-automate
        
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      when: deploy_automate | bool
      
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product infra-server --accept-terms-and-mlsa=true
      when: not deploy_automate | bool
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
        
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: This is a basic migration. For a production environment, you would want to add more error handling, idempotency checks, and possibly use the `command` module with `creates` parameters or the `stat` module to ensure tasks are not unnecessarily repeated.