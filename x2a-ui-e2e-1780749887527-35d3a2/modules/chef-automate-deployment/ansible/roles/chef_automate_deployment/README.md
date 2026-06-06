# Chef Automate Deployment Role

This Ansible role automates the deployment of Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Internet access to download Chef Automate CLI
- Sufficient system resources as required by Chef Automate and Chef Infra Server

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `chef_automate_hostname` | Hostname to set on the target system | `automate.chef.lab` |
| `chef_automate_vm_max_map_count` | Value for vm.max_map_count kernel parameter | `262144` |
| `chef_automate_vm_dirty_expire_centisecs` | Value for vm.dirty_expire_centisecs kernel parameter | `20000` |
| `chef_automate_cli_url` | URL to download Chef Automate CLI | `https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip` |
| `chef_automate_cli_path` | Path to save Chef Automate CLI | `./chef-automate` |
| `chef_automate_accept_terms_and_mlsa` | Whether to accept Chef's terms and MLSA | `true` |
| `chef_automate_products` | List of Chef products to deploy | `['automate', 'infra-server']` |
| `chef_automate_username` | Chef user username | `jtonello` |
| `chef_automate_longusername` | Chef user full name | `John Tonello` |
| `chef_automate_useremail` | Chef user email | `jtonello@chef.lab` |
| `chef_automate_userpassword` | Chef user password | `password` |
| `chef_automate_orgname` | Chef organization short name | `lab` |
| `chef_automate_longorgname` | Chef organization full name | `Chef Lab` |

## AAP Credential Variables

This role uses the following AAP credential variables:

- `username`: Chef user username
- `password`: Chef user password
- `full_name`: Chef user full name
- `email`: Chef user email

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_orgname: 'myorg'
        chef_automate_longorgname: 'My Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef deployment scripts.