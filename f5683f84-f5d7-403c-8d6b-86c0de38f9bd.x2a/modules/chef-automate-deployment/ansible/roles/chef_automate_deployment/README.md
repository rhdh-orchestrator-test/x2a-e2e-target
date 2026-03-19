# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution (Ubuntu 18.04/20.04 recommended)
- Internet connectivity to download Chef Automate CLI
- Sufficient system resources as per Chef Automate requirements

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_automate_hostname | 'automate.chef.lab' | Hostname for the Chef Automate server |
| chef_automate_username | 'jtonello' | Username for the Chef admin user |
| chef_automate_longusername | 'John Tonello' | Full name for the Chef admin user |
| chef_automate_useremail | 'jtonello@chef.lab' | Email for the Chef admin user |
| chef_automate_userpassword | 'password' | Password for the Chef admin user (should be overridden) |
| chef_automate_orgname | 'lab' | Short name for the Chef organization |
| chef_automate_longorgname | 'Chef Lab' | Full name for the Chef organization |
| chef_automate_install_dir | '/root' | Directory where Chef Automate CLI will be installed |
| chef_automate_deploy_with_automate | true | Whether to deploy with Chef Automate (true) or just Chef Server (false) |

## Dependencies

- ansible.posix
- ansible.utils

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  vars:
    chef_automate_hostname: 'chef.example.com'
    chef_automate_username: 'admin'
    chef_automate_longusername: 'Admin User'
    chef_automate_useremail: 'admin@example.com'
    chef_automate_userpassword: 'secure_password'
    chef_automate_orgname: 'myorg'
    chef_automate_longorgname: 'My Organization'
  roles:
    - role: chef_automate_deployment
```

## License

Apache-2.0

## Author Information

Chef Migration Team