# chef_automate_deploy

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution for Chef Automate
- Internet access to download Chef Automate CLI
- Sufficient system resources as per Chef Automate requirements
- Sudo/root access on the target system

## Role Variables

### Default Variables

```yaml
# System configuration
chef_automate_hostname: 'automate.chef.lab'

# Chef Automate CLI
chef_automate_cli_url: 'https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip'
chef_automate_cli_path: './chef-automate'

# Kernel parameters
chef_automate_kernel_params:
  - name: 'vm.max_map_count'
    value: '262144'
  - name: 'vm.dirty_expire_centisecs'
    value: '20000'

# Chef organization details
chef_org_name: 'lab'
chef_org_long_name: 'Chef Lab'

# Deployment options
chef_automate_products:
  - 'automate'
  - 'infra-server'
chef_automate_accept_terms: true
```

### Required Credential Variables

These variables are expected to be provided via AAP credentials:

- `username`: Chef admin username
- `full_name`: Chef admin full name
- `email`: Chef admin email address
- `password`: Chef admin password

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Deploy Chef Automate
  hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deploy
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_org_name: 'example'
        chef_org_long_name: 'Example Organization'
```

## Alternative Usage - Chef Infra Server Only

To deploy only Chef Infra Server without Automate:

```yaml
---
- name: Deploy Chef Infra Server
  hosts: chef_servers
  become: true
  tasks:
    - name: Include chef_automate_deploy role with Infra Server only
      ansible.builtin.include_role:
        name: chef_automate_deploy
        tasks_from: deploy_chef_server
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_org_name: 'example'
        chef_org_long_name: 'Example Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef Automate deployment scripts.