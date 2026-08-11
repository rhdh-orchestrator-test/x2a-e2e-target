---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: Chef Automate Deployment

**TLDR**: This script deploys Chef Automate and Chef Infra Server on a Linux system. It sets system parameters, downloads the Chef Automate CLI, deploys the Chef products, and configures a user and organization. The script is actually a Bash script, not PowerShell, so we'll be migrating from Bash to Ansible.

## Service Type and Configuration

**Service Type**: Configuration Management Server (Chef Automate and Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters for Chef Automate
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server
- Create a Chef user
- Create a Chef organization and associate the user

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
   - Sets up variables for Chef Automate and Chef Infra Server configuration
   - Sets the system hostname using hostnamectl
   - Configures kernel parameters (vm.max_map_count and vm.dirty_expire_centisecs)
   - Downloads and extracts the Chef Automate CLI
   - Deploys Chef Automate and Chef Infra Server with the CLI
   - Creates a Chef user with the specified credentials
   - Creates a Chef organization and associates the user with it
   - Ansible equivalent: Use ansible.builtin.hostname, ansible.posix.sysctl, ansible.builtin.get_url, ansible.builtin.command, and ansible.builtin.shell modules

## PowerShell to Ansible Mapping

Note: Since the original script is Bash, not PowerShell, I'm mapping Bash commands to Ansible modules:

| Bash Command | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Sets the system hostname |
| sysctl -w | ansible.posix.sysctl | Sets kernel parameters |
| curl + gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Downloads and extracts the Chef Automate CLI |
| chmod +x | ansible.builtin.file (mode) | Sets execute permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploys Chef Automate and Chef Infra Server |
| chef-server-ctl user-create | ansible.builtin.command | Creates a Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Creates a Chef organization |

## Dependencies

**PowerShell Module dependencies**: None (original is Bash)
**Windows Features**: None (runs on Linux)
**External packages**: Chef Automate CLI
**Service dependencies**: None explicitly stated

## Checks for the Migration

**Files to verify**: 
- /etc/hostname (modified by hostnamectl)
- ${username}.pem (created by chef-server-ctl user-create)
- ${orgname}-validator.pem (created by chef-server-ctl org-create)

**Registry keys**: None (Linux system)

**Services to check**: 
- Chef Automate service
- Chef Infra Server service

**Firewall rules**: None explicitly configured in the script

## Pre-flight checks:
```
# Check system hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Check Chef Automate status
sudo chef-automate status

# Check Chef Infra Server status
sudo chef-server-ctl status
```

## Ansible Playbook Example

Here's a sample Ansible playbook that would implement the same functionality:

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
        dest: /tmp/chef-automate.gz

    - name: Extract Chef Automate CLI
      ansible.builtin.shell:
        cmd: gunzip -c /tmp/chef-automate.gz > chef-automate
        creates: chef-automate

    - name: Set execute permissions on Chef Automate CLI
      ansible.builtin.file:
        path: chef-automate
        mode: '0755'

    - name: Deploy Chef Automate and Chef Infra Server
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

Note: This playbook assumes you're targeting Linux hosts where Chef Automate will be installed. The `creates` parameters help make the playbook idempotent by preventing re-execution of commands if the specified files already exist.