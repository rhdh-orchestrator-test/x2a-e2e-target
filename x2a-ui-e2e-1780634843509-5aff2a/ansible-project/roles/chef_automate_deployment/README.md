# Chef Automate Deployment Role

This Ansible role automates the deployment of Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Internet connectivity to download Chef Automate CLI
- Sufficient system resources as required by Chef Automate and Chef Infra Server

## Role Variables

### Default Variables

```yaml
# System configuration
chef_automate_hostname: 'automate.chef.lab'

# Chef Automate CLI
chef_automate_cli_url: 'https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip'
chef_automate_cli_path: './chef-automate'

# Chef Automate deployment options
chef_automate_accept_terms: true
chef_automate_products:
  - automate
  - infra-server

# Chef Server organization settings
chef_server_org_name: 'lab'
chef_server_org_long_name: 'Chef Lab'

# File paths for generated keys
chef_server_user_key_path: "{{ username }}.pem"
chef_server_org_key_path: "{{ chef_server_org_name }}-validator.pem"

# System parameters
chef_automate_sysctl_params:
  vm.max_map_count: 262144
  vm.dirty_expire_centisecs: 20000
```

### Required Credential Variables

These variables are expected to be provided via AAP credentials:

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
        chef_server_org_name: 'example'
        chef_server_org_long_name: 'Example Organization'
```

## License

Apache-2.0

## Author Information

Created by the X2A migration tool.