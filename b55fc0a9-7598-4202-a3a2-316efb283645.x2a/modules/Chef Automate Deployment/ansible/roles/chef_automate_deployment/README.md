# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on an on-prem or cloud VM.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Sufficient system resources for Chef Automate and Chef Infra Server
- Internet connectivity to download Chef Automate CLI

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `chef_automate_deploy_with_infra_server` | `true` | Whether to deploy Chef Automate with Chef Infra Server or just Chef Infra Server |
| `chef_automate_hostname` | `automate.chef.lab` | Hostname to set for the Chef Automate server |
| `chef_automate_username` | `jtonello` | Username for the initial Chef user |
| `chef_automate_longusername` | `John Tonello` | Full name for the initial Chef user |
| `chef_automate_useremail` | `jtonello@chef.lab` | Email for the initial Chef user |
| `chef_automate_userpassword` | `password` | Password for the initial Chef user (should be changed) |
| `chef_automate_orgname` | `lab` | Short name for the Chef organization |
| `chef_automate_longorgname` | `Chef Lab` | Full name for the Chef organization |
| `chef_automate_userfilename` | `{{ chef_automate_username }}.pem` | Filename for the user PEM file |
| `chef_automate_orgfilename` | `{{ chef_automate_orgname }}-validator.pem` | Filename for the organization validator PEM file |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_username: 'admin'
        chef_automate_longusername: 'Admin User'
        chef_automate_useremail: 'admin@example.com'
        chef_automate_userpassword: 'secure_password'
        chef_automate_orgname: 'example'
        chef_automate_longorgname: 'Example Organization'
```

## License

Apache-2.0

## Author Information

This role was created as part of the Chef to Ansible migration project.