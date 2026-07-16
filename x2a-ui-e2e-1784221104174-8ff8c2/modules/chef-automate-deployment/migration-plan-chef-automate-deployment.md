---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I need to clarify something important: The files I've found are Bash shell scripts (.sh), not PowerShell (.ps1) scripts. The analysis summary also indicates that no PowerShell files were found (Total files analyzed: 0).

Let me provide a migration plan for converting these Bash scripts to Ansible, as that appears to be what's needed:

# Migration Plan: Chef Automate Deployment

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download the Chef Automate CLI, deploy the products, and create initial users and organizations. The migration will convert these Bash operations to Ansible tasks.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Setting system hostname
- Configuring kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and/or Chef Infra Server
- Creating initial Chef user
- Creating initial Chef organization

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
   - Sets variables for hostname, user details, and organization details
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters for optimal Chef Automate performance
   - Downloads and prepares the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates an initial user with the specified details
   - Creates an organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets the same variables and performs the same system configurations
   - Downloads the Chef Automate CLI but only deploys the Infra Server product
   - Creates the same user and organization structure
   - Ansible equivalent: Same modules as above but with different parameters for the deployment command

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters with immediate effect |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract Chef Automate CLI |
| chmod +x | ansible.builtin.file | Set executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Run Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (these are Bash scripts)
**Windows Features**: None (Linux-based deployment)
**External packages**: curl, gunzip
**Service dependencies**: Chef Automate, Chef Infra Server

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_cores"

# Check if required ports are available
ansible all -m shell -a "ss -tulpn | grep -E '(80|443|9631|9638|9671)'"

# Check disk space
ansible all -m shell -a "df -h /var"
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

For the deploy-chef-server.sh script, you would use the same playbook but modify the deployment command to only include the infra-server product.