# Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported platform for Chef Automate (RHEL/CentOS 7+, Ubuntu 18.04+)
- Minimum system requirements:
  - 4 CPU cores
  - 16GB RAM
  - 60GB free disk space
- Internet connectivity to download Chef Automate CLI

## Role Variables

### Default Variables

```yaml
# Default hostname for Chef Automate
automate_hostname: 'automate.chef.lab'

# User and organization configuration
chef_user:
  username: "{{ username | default('admin') }}"
  full_name: "{{ full_name | default('Administrator') }}"
  email: "{{ email | default('admin@example.com') }}"
  password: "{{ password | default('changeme') }}"

chef_org:
  short_name: 'lab'
  full_name: 'Chef Lab'

# System configuration
kernel_params:
  vm.max_map_count: 262144
  vm.dirty_expire_centisecs: 20000

# Automate CLI download URL
automate_cli_url: "https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip"
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: automate_servers
  become: true
  vars:
    automate_hostname: 'chef-automate.example.com'
    chef_org:
      short_name: 'myorg'
      full_name: 'My Organization'
  roles:
    - role: automate_deployment
```

## AAP Credential Integration

This role is designed to work with AAP credential types. The following credential variables are expected:

- `username`: Chef admin username
- `full_name`: Chef admin full name
- `email`: Chef admin email address
- `password`: Chef admin password

## License

Apache 2.0

## Author Information

Created by Chef to Ansible Migration Tool