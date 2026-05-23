# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Sufficient disk space for Chef Automate installation (at least 5GB recommended)
- Internet connectivity to download Chef Automate packages

## Role Variables

### Default Variables

```yaml
# System configuration
chef_automate_hostname: 'automate.chef.lab'
chef_automate_sysctl_settings:
  vm.max_map_count: 262144
  vm.dirty_expire_centisecs: 20000

# Chef Automate installation
chef_automate_cli_url: 'https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip'
chef_automate_cli_path: '/tmp/chef-automate'
chef_automate_accept_terms: true
chef_automate_products:
  - automate
  - infra-server

# User and organization setup
chef_automate_username: 'jtonello'
chef_automate_user_fullname: 'John Tonello'
chef_automate_user_email: 'jtonello@chef.lab'
chef_automate_org_name: 'lab'
chef_automate_org_fullname: 'Chef Lab'
```

### AAP Credential Variables

When using this role with Ansible Automation Platform, the following credential variables can be provided:

- `username`: Chef user username
- `full_name`: Chef user's full name
- `email`: Chef user's email address
- `password`: Chef user's password

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Deploy Chef Automate
  hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_products:
          - automate
          - infra-server
```

## License

Apache-2.0

## Author Information

Migrated from Chef deployment scripts.