# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and/or Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution for Chef Automate
- Sufficient disk space (at least 40GB recommended)
- Minimum 4GB RAM
- Internet connectivity to download Chef Automate CLI

## Role Variables

### Default Variables

```yaml
# Default variables for Chef Automate deployment
chef_automate_hostname: 'automate.chef.lab'
chef_automate_username: 'jtonello'
chef_automate_longusername: 'John Tonello'
chef_automate_useremail: 'jtonello@chef.lab'
# Password is provided via AAP credential variable: {{ user_password }}
chef_automate_orgname: 'lab'
chef_automate_longorgname: 'Chef Lab'

# System configuration
chef_automate_vm_max_map_count: 262144
chef_automate_vm_dirty_expire_centisecs: 20000

# Chef Automate CLI download URL
chef_automate_cli_url: 'https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip'

# File paths
chef_automate_cli_path: './chef-automate'
chef_automate_user_key_path: './{{ chef_automate_username }}.pem'
chef_automate_org_key_path: './{{ chef_automate_orgname }}-validator.pem'
```

### Deployment Type Variable

```yaml
# Set deployment type - options: 'automate' or 'chef-server'
chef_deploy_type: 'automate'  # Default is to deploy both Automate and Chef Infra Server
```

## AAP Credential Variables

This role uses the following credential variables that should be provided via AAP:

- `{{ username }}` - Alternative to chef_automate_username if needed
- `{{ user_email }}` - Alternative to chef_automate_useremail if needed
- `{{ user_password }}` - Password for the Chef user (required)

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Deploy Chef Automate and Chef Infra Server
  hosts: chef_servers
  become: true
  vars:
    chef_automate_hostname: 'chef.example.com'
    chef_automate_username: 'admin'
    chef_automate_longusername: 'Admin User'
    chef_automate_useremail: 'admin@example.com'
    chef_automate_orgname: 'example'
    chef_automate_longorgname: 'Example Organization'
    chef_deploy_type: 'automate'  # Deploy both Automate and Chef Infra Server
  roles:
    - role: chef_automate_deployment
```

## License

Apache-2.0

## Author Information

Migrated from Chef Automate deployment scripts.