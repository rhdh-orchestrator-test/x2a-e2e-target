# Chef Deployment Role

This Ansible role automates the deployment of Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Sufficient disk space for Chef Automate and Chef Infra Server installation
- Internet connectivity to download Chef packages

## Role Variables

### Default Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `chef_hostname` | Hostname to set on the target system | `automate.chef.lab` |
| `chef_sysctl_settings` | Kernel parameters required for Chef Automate | See defaults/main.yml |
| `chef_automate_cli_url` | URL to download Chef Automate CLI | See defaults/main.yml |
| `chef_deploy_automate` | Whether to deploy Chef Automate along with Chef Infra Server | `true` |
| `chef_accept_terms_and_mlsa` | Accept Chef license terms | `true` |
| `chef_username` | Username for the initial Chef user | `jtonello` |
| `chef_user_fullname` | Full name for the initial Chef user | `John Tonello` |
| `chef_user_email` | Email for the initial Chef user | `jtonello@chef.lab` |
| `chef_org_name` | Name for the initial Chef organization | `lab` |
| `chef_org_fullname` | Full name for the initial Chef organization | `Chef Lab` |

### Required AAP Credential Variables

| Variable | Description |
|----------|-------------|
| `user_password` | Password for the initial Chef user |

## Dependencies

None.

## Example Playbook

```yaml
---
- hosts: chef_servers
  become: true
  roles:
    - role: chef_deployment
      vars:
        chef_hostname: 'chef.example.com'
        chef_username: 'admin'
        chef_user_fullname: 'Admin User'
        chef_user_email: 'admin@example.com'
        chef_org_name: 'example'
        chef_org_fullname: 'Example Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef deployment scripts.