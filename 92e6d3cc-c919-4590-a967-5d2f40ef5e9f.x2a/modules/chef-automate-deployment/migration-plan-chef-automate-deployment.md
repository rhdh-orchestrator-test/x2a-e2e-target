---
source-path: setup-automate
---

Based on my analysis, I'll now create a migration plan for converting these Chef Automate deployment scripts to Ansible.

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. They set system parameters, download the Chef Automate CLI, deploy the Chef products, and create initial users and organizations. The scripts are designed for on-premises or cloud VM deployments.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate/Chef Infra Server)

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
   - Sets system hostname using `hostnamectl`
   - Configures kernel parameters with `sysctl` for optimal Chef Automate performance
   - Downloads and prepares Chef Automate CLI
   - Deploys both Chef Automate and Chef Infra Server products
   - Creates initial admin user with specified credentials
   - Creates organization and associates admin user
   - Ansible equivalent: Use `ansible.builtin.hostname`, `ansible.posix.sysctl`, `ansible.builtin.get_url`, `ansible.builtin.command` modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server (without Automate)
   - Sets system hostname using `hostnamectl`
   - Configures kernel parameters with `sysctl`
   - Downloads and prepares Chef Automate CLI
   - Deploys only Chef Infra Server product
   - Creates initial admin user with specified credentials
   - Creates organization and associates admin user
   - Ansible equivalent: Same modules as above but with different parameters for the deployment command

## PowerShell to Ansible Mapping

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

**PowerShell Module dependencies**: None (these are Bash scripts)
**Windows Features**: None (Linux-based deployment)
**External packages**: curl, gunzip
**Service dependencies**: None specified in scripts

## Checks for the Migration

**Files to verify**: 
- `/etc/hostname` (modified by hostnamectl)
- `${username}.pem` (user key file)
- `${orgname}-validator.pem` (organization validator key)

**Registry keys**: None (Linux-based deployment)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

**Firewall rules**: None specified in scripts (would need to be added separately)

## Pre-flight checks:
```
# Check system requirements
ansible all -m setup -a "filter=ansible_memtotal_mb,ansible_processor_cores"

# Verify hostname resolution
ansible all -m command -a "getent hosts {{ chef_automate_hostname }}"

# Check required ports are available
ansible all -m wait_for -a "port=443 timeout=1" || echo "Port 443 is available"

# Check disk space
ansible all -m shell -a "df -h / | awk 'NR==2 {print $4}'"
```

## Ansible Playbook Example

Here's a starting point for your Ansible playbook:

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
    - name: Set system hostname
      ansible.builtin.hostname:
        name: "{{ hostname }}"
      
    - name: Configure kernel parameters for Chef Automate
      ansible.posix.sysctl:
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        state: present
        reload: yes
      loop:
        - { key: 'vm.max_map_count', value: '262144' }
        - { key: 'vm.dirty_expire_centisecs', value: '20000' }
      
    - name: Download Chef Automate CLI
      ansible.builtin.get_url:
        url: https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip
        dest: /tmp/chef-automate_linux_amd64.zip
        mode: '0644'
      
    - name: Extract Chef Automate CLI
      ansible.builtin.shell: gunzip -c /tmp/chef-automate_linux_amd64.zip > /tmp/chef-automate
      args:
        creates: /tmp/chef-automate
      
    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: /tmp/chef-automate
        mode: '0755'
      
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      when: deploy_automate | bool
      args:
        creates: /hab
      
    - name: Deploy Chef Infra Server only
      ansible.builtin.command:
        cmd: /tmp/chef-automate deploy --product infra-server --accept-terms-and-mlsa=true
      when: not deploy_automate | bool
      args:
        creates: /hab
      
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

This playbook provides a direct translation of the Bash scripts to Ansible, maintaining the same functionality while adding idempotence through Ansible's built-in state management.