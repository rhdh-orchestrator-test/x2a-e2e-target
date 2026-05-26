# Chef Deployment Role

This Ansible role deploys Chef Automate and/or Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Internet access to download Chef Automate CLI
- Sufficient system resources for Chef Automate and Chef Infra Server

## Role Variables

### Default Variables

```yaml
# Deployment flags
chef_deploy_automate: true
chef_deploy_chef_server: false

# Hostname configuration
chef_hostname: 'automate.chef.lab'

# System parameters
chef_vm_max_map_count: 262144
chef_vm_dirty_expire_centisecs: 20000

# Chef Automate CLI
chef_automate_cli_url: 'https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip'
chef_automate_cli_path: './chef-automate'

# Organization settings
chef_org_name: 'lab'
chef_org_long_name: 'Chef Lab'

# File paths for keys
chef_user_key_filename: "{{ username }}.pem"
chef_org_validator_filename: "{{ chef_org_name }}-validator.pem"

# Deploy options
chef_accept_terms_and_mlsa: true
```

### AAP Credential Variables

This role uses the following AAP credential variables:

- `username`: Username for the Chef user
- `full_name`: Full name for the Chef user
- `email`: Email address for the Chef user
- `password`: Password for the Chef user

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_deployment
      vars:
        chef_hostname: 'chef.example.com'
        chef_deploy_automate: true
        chef_deploy_chef_server: false
```

## License

Apache-2.0

## Author Information

Migrated from Chef deployment scripts.