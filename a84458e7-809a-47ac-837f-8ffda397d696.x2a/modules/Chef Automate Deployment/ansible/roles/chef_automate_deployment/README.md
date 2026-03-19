# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and/or Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Internet access to download Chef Automate CLI
- Sufficient system resources for Chef Automate and Chef Infra Server

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `chef_automate_deploy_with_infra_server` | `true` | When true, deploys both Chef Automate and Chef Infra Server. When false, deploys only Chef Infra Server |
| `chef_automate_hostname` | `automate.chef.lab` | Hostname to set on the target system |
| `chef_automate_username` | `jtonello` | Admin username to create |
| `chef_automate_longusername` | `John Tonello` | Full name for the admin user |
| `chef_automate_useremail` | `jtonello@chef.lab` | Email address for the admin user |
| `chef_automate_userpassword` | `password` | Password for the admin user (should be vaulted in production) |
| `chef_automate_orgname` | `lab` | Organization short name |
| `chef_automate_longorgname` | `Chef Lab` | Organization full name |
| `chef_automate_userfilename` | `{{ chef_automate_username }}.pem` | Filename for the user's PEM key |
| `chef_automate_orgfilename` | `{{ chef_automate_orgname }}-validator.pem` | Filename for the organization validator PEM key |

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_username: 'admin'
        chef_automate_userpassword: 'secure_password'
        chef_automate_orgname: 'myorg'
```

## Deploy Chef Infra Server Only

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_deploy_with_infra_server: false
        chef_automate_hostname: 'chef.example.com'
```

## License

Apache 2.0

## Author Information

Migrated from Chef deployment scripts