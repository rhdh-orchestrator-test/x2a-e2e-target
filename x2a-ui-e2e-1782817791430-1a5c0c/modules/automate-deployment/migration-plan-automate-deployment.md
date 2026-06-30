---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I don't see any PowerShell files in the provided directories. The files in setup-automate are Bash shell scripts, not PowerShell scripts. Let me provide a migration plan based on the Bash scripts I found, as they appear to be what you want to migrate to Ansible.

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: The scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download and install Chef Automate CLI, deploy Chef products, and create initial users and organizations. These are Bash scripts, not PowerShell, so the migration will be from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters for Chef Automate
- Download and install Chef Automate CLI
- Deploy Chef Automate and/or Chef Infra Server
- Create initial Chef user
- Create initial Chef organization
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
   - Sets configurable variables for hostname, user details, and organization details
   - Sets system hostname using hostnamectl
   - Configures kernel parameters using sysctl
   - Downloads Chef Automate CLI using curl
   - Deploys Chef Automate and Chef Infra Server
   - Creates initial Chef user with admin privileges
   - Creates Chef organization and associates the admin user
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets the same variables and follows the same process
   - Ansible equivalent: Same modules as above but with different parameters for the deploy command

## PowerShell to Ansible Mapping

Since these are Bash scripts, not PowerShell, I'll provide a Bash to Ansible mapping:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (these are Bash scripts)
**Windows Features**: None (these are Linux scripts)
**External packages**: curl, gunzip
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- ${username}.pem
- ${orgname}-validator.pem

**Registry keys**: None (Linux system)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

**Firewall rules**: 
- Port 443 (HTTPS) should be open for Chef Automate UI
- Port 9631 (Habitat Supervisor) should be open

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_cores"

# Check if required ports are available
ansible all -m shell -a "ss -tulpn | grep -E '443|9631'"

# Check kernel parameters
ansible all -m shell -a "sysctl vm.max_map_count vm.dirty_expire_centisecs"

# Check disk space
ansible all -m shell -a "df -h /"
```

## Ansible Playbook Example

Here's a starting point for your Ansible playbook:

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
      
    - name: Set kernel parameter vm.max_map_count
      ansible.posix.sysctl:
        name: vm.max_map_count
        value: '262144'
        state: present
        sysctl_set: yes
        
    - name: Set kernel parameter vm.dirty_expire_centisecs
      ansible.posix.sysctl:
        name: vm.dirty_expire_centisecs
        value: '20000'
        state: present
        sysctl_set: yes
        
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate.zip
        
    - name: Extract Chef Automate CLI
      ansible.builtin.unarchive:
        src: /tmp/chef-automate.zip
        dest: /tmp/
        remote_src: yes
        
    - name: Move Chef Automate CLI to current directory
      ansible.builtin.copy:
        src: /tmp/chef-automate
        dest: ./chef-automate
        remote_src: yes
        mode: '0755'
        
    - name: Deploy Chef Automate and Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
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

Note: This playbook is a starting point and may need adjustments based on your specific environment and requirements. Sensitive information like passwords should be handled securely using Ansible Vault.