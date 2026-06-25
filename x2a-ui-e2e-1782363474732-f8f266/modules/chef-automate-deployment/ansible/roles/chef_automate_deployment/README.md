# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Internet connectivity to download Chef Automate CLI
- Sufficient system resources for Chef Automate and Chef Infra Server

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `chef_automate_hostname` | Hostname to set on the target system | `automate.chef.lab` |
| `chef_automate_cli_url` | URL to download Chef Automate CLI | `https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip` |
| `chef_automate_sysctl_params` | Dictionary of kernel parameters to set | See defaults/main.yml |
| `chef_user_name` | Chef user name | From AAP credential or `chefuser` |
| `chef_user_fullname` | Chef user's full name | From AAP credential or `Chef User` |
| `chef_user_email` | Chef user's email | From AAP credential or `chef@example.com` |
| `chef_user_password` | Chef user's password | From AAP credential or `changeme` |
| `chef_org_name` | Chef organization short name | `lab` |
| `chef_org_fullname` | Chef organization full name | `Chef Lab` |
| `chef_automate_deploy_automate` | Whether to deploy Chef Automate | `true` |
| `chef_automate_deploy_infra_server` | Whether to deploy Chef Infra Server | `true` |
| `chef_automate_accept_terms` | Whether to accept Chef terms | `true` |

## Dependencies

- eloy.redis (optional, if Redis is used as a backend component)

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_org_name: 'myorg'
        chef_org_fullname: 'My Organization'
```

## AAP Credential Integration

This role is designed to work with AAP credential types. The following credential variables are used:

- `username`: Chef user name
- `full_name`: Chef user's full name
- `email`: Chef user's email
- `password`: Chef user's password

## License

Apache-2.0

## Author Information

Ansible Automation Platform Team