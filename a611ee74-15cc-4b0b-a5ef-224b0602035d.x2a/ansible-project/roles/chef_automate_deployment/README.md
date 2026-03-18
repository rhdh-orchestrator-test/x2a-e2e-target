# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Sufficient system resources (minimum 4 CPU cores, 16GB RAM, 60GB disk)
- Internet connectivity to download Chef packages

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_automate_deployment_type | 'automate' | Deployment type: 'automate' for Chef Automate with Infra Server, 'chef_server' for Chef Infra Server only |
| chef_automate_hostname | 'automate.chef.lab' | Hostname for the Chef Automate/Infra Server |
| chef_automate_username | 'jtonello' | Admin username to create |
| chef_automate_longusername | 'John Tonello' | Full name for the admin user |
| chef_automate_useremail | 'jtonello@chef.lab' | Email for the admin user |
| chef_automate_userpassword | 'password' | Password for the admin user (should be overridden) |
| chef_automate_orgname | 'lab' | Organization short name |
| chef_automate_longorgname | 'Chef Lab' | Organization full name |

## Dependencies

- ansible.posix collection (for sysctl module)
- community.general collection

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  vars:
    chef_automate_hostname: 'chef.example.com'
    chef_automate_userpassword: 'secure_password'
  roles:
    - role: chef_automate_deployment
```

## License

Apache-2.0

## Author Information

Your Organization