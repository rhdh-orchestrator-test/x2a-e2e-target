# Chef Automate Deployment Role

This Ansible role automates the deployment of Chef Automate and Chef Infra Server on an on-premises or cloud VM.

## Requirements

- Target system must be a supported Linux distribution (RHEL/CentOS 7+, Ubuntu 18.04+)
- Internet connectivity to download Chef Automate CLI
- Sufficient system resources as per Chef Automate requirements:
  - 4+ CPU cores
  - 16+ GB RAM
  - 60+ GB free disk space

## Role Variables

### Required Variables (from AAP Credentials)

These variables are injected by AAP credential types at runtime:

- `username`: Chef admin username
- `full_name`: Chef admin user's full name
- `email`: Chef admin user's email address
- `password`: Chef admin user's password

### Default Variables

```yaml
# System configuration
chef_automate_hostname: 'automate.chef.lab'

# Kernel parameters
chef_automate_vm_max_map_count: 262144
chef_automate_vm_dirty_expire_centisecs: 20000

# Chef Automate CLI
chef_automate_cli_url: "https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip"
chef_automate_cli_path: "/tmp/chef-automate"

# Deployment options
chef_automate_accept_terms: true
chef_automate_deploy_automate: true
chef_automate_deploy_infra_server: true

# Organization settings
chef_automate_org_name: 'lab'
chef_automate_org_long_name: 'Chef Lab'

# File paths for keys
chef_automate_user_key_path: "{{ ansible_env.HOME }}/{{ username }}.pem"
chef_automate_org_key_path: "{{ ansible_env.HOME }}/{{ chef_automate_org_name }}-validator.pem"
```

## Dependencies

- eloy.redis (1.0.0) - Optional, if Redis is needed as a component

## Example Playbook

```yaml
---
- name: Deploy Chef Automate and Infra Server
  hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_org_name: 'example'
        chef_automate_org_long_name: 'Example Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef Automate deployment scripts