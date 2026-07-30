---
source-path: setup-automate/deploy-automate.sh
---

Now I'll create a migration plan based on the files I've found:

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: These scripts deploy Chef Automate and Chef Infra Server on Linux systems. The scripts set system parameters, download Chef Automate CLI, deploy the products, and create initial users and organizations. The migration will convert these Bash scripts to Ansible playbooks that perform equivalent operations.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server (Configuration Management)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
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

## Module Explanation

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Sets system hostname using `hostnamectl`
   - Configures kernel parameters using `sysctl`
   - Downloads Chef Automate CLI using `curl` and makes it executable
   - Deploys Chef Automate and Chef Infra Server with `chef-automate deploy`
   - Creates a Chef user with `chef-server-ctl user-create`
   - Creates a Chef organization with `chef-server-ctl org-create`
   - Ansible equivalent: Use `hostname`, `sysctl`, `get_url`, `command`, and custom modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Similar to deploy-automate.sh but only deploys Chef Infra Server without Automate
   - Sets system hostname using `hostnamectl`
   - Configures kernel parameters using `sysctl`
   - Downloads Chef Automate CLI using `curl` and makes it executable
   - Deploys only Chef Infra Server with `chef-automate deploy --product infra-server`
   - Creates a Chef user with `chef-server-ctl user-create`
   - Creates a Chef organization with `chef-server-ctl org-create`
   - Ansible equivalent: Same modules as above with different parameters

## PowerShell to Ansible Mapping

Note: These are actually Bash scripts, not PowerShell. Here's the mapping to Ansible:

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url | Downloads Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets executable permissions |
| chef-automate deploy | ansible.builtin.command | Runs Chef Automate deployment |
| chef-server-ctl user-create | ansible.builtin.command | Creates Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates Chef organization |

## Dependencies

**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated, but Chef Automate has its own dependencies

## Checks for the Migration

**Files to verify**: 
- `/etc/hostname` (modified by hostnamectl)
- User PEM file (e.g., `jtonello.pem`)
- Organization validator PEM file (e.g., `lab-validator.pem`)

**Services to check**: 
- Chef Automate services
- Chef Infra Server services

## Pre-flight checks:
```yaml
- name: Check system requirements
  ansible.builtin.command: grep MemTotal /proc/meminfo
  register: meminfo
  changed_when: false

- name: Verify system has enough memory (at least 8GB recommended for Chef Automate)
  ansible.builtin.assert:
    that: 
      - (meminfo.stdout_lines[0] | regex_replace('MemTotal:\\s+([0-9]+) kB', '\\1') | int) > 8000000
    fail_msg: "System does not have enough memory for Chef Automate"
    success_msg: "System has sufficient memory"

- name: Check disk space
  ansible.builtin.command: df -h /
  register: diskspace
  changed_when: false
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace the `deploy-automate.sh` script:

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
    - name: Set system hostname
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
    
    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
        creates: /hab
      register: deploy_result
      
    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
        creates: "{{ userfilename }}"
      
    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
        creates: "{{ orgfilename }}"
```

Note: For security reasons, you should consider using Ansible Vault for sensitive information like passwords in the actual implementation.