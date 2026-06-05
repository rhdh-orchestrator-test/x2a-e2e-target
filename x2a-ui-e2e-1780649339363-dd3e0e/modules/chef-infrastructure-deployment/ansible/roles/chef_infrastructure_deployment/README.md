# Chef Infrastructure Deployment Role

This Ansible role deploys Chef Automate and/or Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution for Chef Automate and Chef Infra Server
- Sufficient disk space and memory for Chef Automate and Chef Infra Server
- Internet connectivity to download Chef Automate CLI

## Role Variables

### Default Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_hostname | 'automate.chef.lab' | Hostname to set on the target system |
| chef_vm_max_map_count | 262144 | Kernel parameter for vm.max_map_count |
| chef_vm_dirty_expire_centisecs | 20000 | Kernel parameter for vm.dirty_expire_centisecs |
| chef_automate_cli_url | URL | URL to download Chef Automate CLI |
| chef_org_name | 'lab' | Chef organization short name |
| chef_org_long_name | 'Chef Lab' | Chef organization long name |
| chef_user_name | From AAP credentials | Chef admin user name |
| chef_user_long_name | 'Chef Administrator' | Chef admin user full name |
| chef_user_email | 'admin@example.com' | Chef admin user email |
| chef_deploy_automate | true | Whether to deploy Chef Automate with Chef Infra Server |

### AAP Credential Variables

This role expects the following credential variables to be injected by AAP:

- `username`: Chef admin username
- `password`: Chef admin password

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  vars:
    chef_hostname: 'chef.example.com'
    chef_org_name: 'example'
    chef_org_long_name: 'Example Organization'
    chef_deploy_automate: true
  roles:
    - role: chef_infrastructure_deployment
```

## License

Apache-2.0

## Author Information

Migrated from Chef scripts to Ansible role.