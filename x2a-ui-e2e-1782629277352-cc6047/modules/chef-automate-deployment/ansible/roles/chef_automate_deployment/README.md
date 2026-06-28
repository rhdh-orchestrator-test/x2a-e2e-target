# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported platform for Chef Automate and Chef Infra Server
- Sufficient disk space and memory for Chef Automate requirements
- Internet access to download Chef Automate CLI

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| chef_automate_hostname | Hostname for the Chef Automate server | automate.chef.lab |
| chef_automate_orgname | Short name for the Chef organization | lab |
| chef_automate_longorgname | Full name for the Chef organization | Chef Lab |
| chef_automate_vm_max_map_count | Kernel parameter for vm.max_map_count | 262144 |
| chef_automate_vm_dirty_expire_centisecs | Kernel parameter for vm.dirty_expire_centisecs | 20000 |
| chef_automate_cli_url | URL to download Chef Automate CLI | https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip |
| chef_automate_products | List of Chef products to deploy | [automate, infra-server] |
| chef_automate_accept_terms | Whether to accept Chef terms and MLSA | true |

## AAP Credential Variables

This role uses the following AAP credential variables:

- `username`: Chef user's username
- `full_name`: Chef user's full name
- `email`: Chef user's email address
- `password`: Chef user's password

## Example Playbook

```yaml
- hosts: chef_servers
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: "chef.example.com"
        chef_automate_orgname: "example"
        chef_automate_longorgname: "Example Organization"
```

## License

Apache 2.0

## Author Information

Created by X2A Migration Tool