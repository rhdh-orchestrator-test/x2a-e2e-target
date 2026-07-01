---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys the Chef Automate and Infra Server products, and creates a user and organization in the Chef Server. The script is actually a Bash script, not PowerShell, so we'll be migrating from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Chef Automate and Chef Infra Server

**Key Operations**:
- Setting the system hostname
- Configuring kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
- Downloading and installing Chef Automate CLI
- Deploying Chef Automate and Chef Infra Server
- Creating a Chef user
- Creating a Chef organization and associating the user with it

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
   - Configures kernel parameters using sysctl
   - Downloads and extracts the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server
   - Creates a user in Chef Server
   - Creates an organization in Chef Server and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts the Chef Automate CLI |
| chmod +x | ansible.builtin.file | Sets executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Chef Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates a user in Chef Server |
| chef-server-ctl org-create | ansible.builtin.command | Creates an organization in Chef Server |

## Dependencies

**PowerShell Module dependencies**: None (script is Bash, not PowerShell)
**Windows Features**: None (Linux-based deployment)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly defined in the script

## Checks for the Migration

**Files to verify**: 
- /etc/hostname
- chef-automate executable
- User PEM file (e.g., jtonello.pem)
- Organization validator PEM file (e.g., lab-validator.pem)

**Registry keys**: None (Linux-based deployment)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: None explicitly defined in the script

## Pre-flight checks:
```
# Check system requirements
- Verify minimum RAM (8GB recommended)
- Verify minimum CPU (4 cores recommended)
- Verify minimum disk space (40GB recommended)
- Verify network connectivity to packages.chef.io
- Verify hostname resolution
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would replace the Bash script:

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
        dest: /tmp/chef-automate.zip
        mode: '0644'

    - name: Extract Chef Automate CLI
      ansible.builtin.command:
        cmd: gunzip -c /tmp/chef-automate.zip > chef-automate
        creates: chef-automate
      args:
        chdir: "{{ ansible_env.HOME }}"

    - name: Make Chef Automate CLI executable
      ansible.builtin.file:
        path: "{{ ansible_env.HOME }}/chef-automate"
        mode: '0755'

    - name: Deploy Chef Automate and Chef Infra Server
      ansible.builtin.command:
        cmd: ./chef-automate deploy --product automate --product infra-server --accept-terms-and-mlsa=true
      args:
        chdir: "{{ ansible_env.HOME }}"
        creates: /hab

    - name: Create Chef user
      ansible.builtin.command:
        cmd: chef-server-ctl user-create {{ username }} {{ longusername }} {{ useremail }} "{{ userpassword }}" --filename {{ userfilename }}
      args:
        chdir: "{{ ansible_env.HOME }}"
        creates: "{{ ansible_env.HOME }}/{{ userfilename }}"

    - name: Create Chef organization
      ansible.builtin.command:
        cmd: chef-server-ctl org-create {{ orgname }} "{{ longorgname }}" --association_user {{ username }} --filename {{ orgfilename }}
      args:
        chdir: "{{ ansible_env.HOME }}"
        creates: "{{ ansible_env.HOME }}/{{ orgfilename }}"
```

Note: This playbook assumes you're running it against a host group called `chef_servers`. You would need to adjust the `hosts` parameter to match your inventory. Also, sensitive information like passwords should be handled using Ansible Vault in a production environment.