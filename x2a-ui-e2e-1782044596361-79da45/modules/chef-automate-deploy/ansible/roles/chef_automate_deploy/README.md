# Chef Automate Deploy

This role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution for Chef Automate
- Internet access to download Chef Automate CLI
- Sufficient system resources (RAM, CPU, disk) for Chef Automate
- Sudo/root access on the target system

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| chef_automate_hostname | Hostname to set for the Chef Automate server | automate.chef.lab |
| chef_automate_vm_max_map_count | Kernel parameter for vm.max_map_count | 262144 |
| chef_automate_vm_dirty_expire_centisecs | Kernel parameter for vm.dirty_expire_centisecs | 20000 |
| chef_automate_cli_url | URL to download Chef Automate CLI | https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip |
| chef_automate_cli_path | Path to save Chef Automate CLI | /tmp/chef-automate |
| chef_automate_products | List of Chef products to deploy | [automate, infra-server] |
| chef_automate_accept_terms | Whether to accept Chef terms and MLSA | true |
| chef_automate_username | Chef admin username | jtonello |
| chef_automate_longusername | Chef admin full name | John Tonello |
| chef_automate_useremail | Chef admin email | jtonello@chef.lab |
| chef_automate_orgname | Chef organization short name | lab |
| chef_automate_longorgname | Chef organization full name | Chef Lab |
| chef_automate_user_key_path | Path to save user key | /tmp/{{ chef_automate_username }}.pem |
| chef_automate_org_key_path | Path to save organization validator key | /tmp/{{ chef_automate_orgname }}-validator.pem |

## AAP Credential Variables

This role uses the following AAP credential variables:

- `username`: Chef admin username
- `full_name`: Chef admin full name
- `email`: Chef admin email
- `password`: Chef admin password

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  roles:
    - role: chef_automate_deploy
      vars:
        chef_automate_hostname: 'chef.example.com'
```

## License

Apache 2.0

## Author Information

Migrated from Chef Automate deployment scripts.