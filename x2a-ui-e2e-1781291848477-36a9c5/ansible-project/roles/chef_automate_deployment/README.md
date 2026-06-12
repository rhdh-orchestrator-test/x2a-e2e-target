# Chef Automate Deployment Role

This Ansible role automates the deployment of Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported platform for Chef Automate and Chef Infra Server
- Sufficient disk space (at least 40GB recommended)
- Minimum 8GB RAM
- Internet connectivity to download Chef Automate CLI

## Role Variables

### Default Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `chef_automate_hostname` | Hostname to set on the target system | `automate.chef.lab` |
| `chef_automate_cli_url` | URL to download Chef Automate CLI | `https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip` |
| `chef_automate_sysctl_params` | Kernel parameters to set for optimal performance | See `defaults/main.yml` |
| `chef_automate_accept_terms` | Whether to accept Chef's terms and MLSA | `true` |
| `chef_automate_products` | List of Chef products to deploy | `['automate', 'infra-server']` |
| `chef_org_name` | Short name for the Chef organization | `lab` |
| `chef_org_fullname` | Full name for the Chef organization | `Chef Lab` |

### Credential Variables

The following variables are expected to be provided via AAP credentials:

| Variable | Description |
|----------|-------------|
| `username` | Chef user name |
| `password` | Chef user password |
| `full_name` | Chef user's full name |
| `email` | Chef user's email address |

## Dependencies

None.

## Example Playbook

```yaml
---
- hosts: chef_servers
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_org_name: 'myorg'
        chef_org_fullname: 'My Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef Automate deployment scripts.