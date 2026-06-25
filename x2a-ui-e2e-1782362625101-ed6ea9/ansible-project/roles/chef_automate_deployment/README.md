# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported platform for Chef Automate and Chef Infra Server
- Sufficient disk space (at least 40GB recommended)
- Minimum 4GB RAM
- Internet connectivity to download Chef Automate CLI

## Role Variables

### Default Variables (can be overridden)

```yaml
# Deployment options
deploy_automate: true  # Set to false to deploy only Chef Infra Server
accept_terms_and_mlsa: true

# File paths
chef_automate_binary_path: "{{ ansible_env.HOME }}/chef-automate"
user_key_filename: "{{ username }}.pem"
org_validator_filename: "{{ orgname }}-validator.pem"
```

### Required Variables (provided by AAP credentials)

```yaml
username: 'username'  # Chef user username
full_name: 'Full Name'  # Chef user full name
email: 'user@example.com'  # Chef user email
password: 'password'  # Chef user password
```

### Other Variables

```yaml
hostname: 'automate.chef.lab'  # Hostname for the Chef Automate server
orgname: 'lab'  # Chef organization short name
longorgname: 'Chef Lab'  # Chef organization full name
vm_max_map_count: 262144  # System parameter for Elasticsearch
vm_dirty_expire_centisecs: 20000  # System parameter for performance
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  roles:
    - role: chef_automate_deployment
      vars:
        hostname: 'chef.example.com'
        orgname: 'myorg'
        longorgname: 'My Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef Automate deployment scripts.