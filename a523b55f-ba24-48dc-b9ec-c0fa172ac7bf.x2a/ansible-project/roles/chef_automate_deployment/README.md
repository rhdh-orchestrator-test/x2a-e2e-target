# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Ansible 2.9 or higher
- ansible.posix collection

## Role Variables

### Deployment Options

| Variable | Default | Description |
|----------|---------|-------------|
| `chef_automate_deploy_automate` | `true` | Whether to deploy Chef Automate with Chef Infra Server |
| `chef_automate_deploy_chef_server` | `false` | Whether to deploy Chef Infra Server only |
| `chef_automate_install_dir` | `/opt/chef-automate` | Directory where Chef Automate CLI will be installed |

### Chef Automate Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `chef_automate_hostname` | `automate.chef.lab` | Hostname for the Chef Automate server |
| `chef_automate_username` | `jtonello` | Username for the initial Chef user |
| `chef_automate_longusername` | `John Tonello` | Full name for the initial Chef user |
| `chef_automate_useremail` | `jtonello@chef.lab` | Email for the initial Chef user |
| `chef_automate_userpassword` | `password` | Password for the initial Chef user |
| `chef_automate_orgname` | `lab` | Short name for the Chef organization |
| `chef_automate_longorgname` | `Chef Lab` | Full name for the Chef organization |

### Generated Files

| Variable | Default | Description |
|----------|---------|-------------|
| `chef_automate_userfilename` | `{{ chef_automate_username }}.pem` | Path to save the user key file |
| `chef_automate_orgfilename` | `{{ chef_automate_orgname }}-validator.pem` | Path to save the organization validator key file |

## Dependencies

This role requires the ansible.posix collection for sysctl operations.

## Example Playbook

```yaml
---
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_username: 'admin'
        chef_automate_userpassword: 'secure_password'
```

## License

Apache-2.0

## Author Information

Ansible Migration Team