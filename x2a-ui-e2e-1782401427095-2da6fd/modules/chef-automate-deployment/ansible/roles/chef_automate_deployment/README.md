# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution for Chef Automate
- Sufficient disk space (at least 40GB recommended)
- Minimum 4GB RAM
- Internet connectivity to download Chef Automate packages

## Role Variables

### Default Variables

```yaml
# Default hostname for Chef Automate server
chef_automate_hostname: 'automate.chef.lab'

# URL to download Chef Automate CLI
chef_automate_download_url: 'https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip'

# Path where Chef Automate binary will be saved
chef_automate_binary_path: './chef-automate'

# System configuration parameters
chef_automate_sysctl_params:
  vm.max_map_count: 262144
  vm.dirty_expire_centisecs: 20000

# Chef Automate deployment options
chef_automate_accept_terms: true
chef_automate_products:
  - automate
  - infra-server

# Set to true to deploy only Chef Infra Server without Automate
chef_server_only: false

# Organization settings
chef_org_name: 'lab'
chef_org_full_name: 'Chef Lab'
```

### Required AAP Credential Variables

This role requires the following credential variables to be provided via AAP:

- `username`: Chef user username
- `full_name`: Chef user's full name
- `email`: Chef user's email address
- `password`: Chef user's password

## Dependencies

None.

## Example Playbook

```yaml
---
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_org_name: 'example'
        chef_org_full_name: 'Example Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef Automate deployment scripts.