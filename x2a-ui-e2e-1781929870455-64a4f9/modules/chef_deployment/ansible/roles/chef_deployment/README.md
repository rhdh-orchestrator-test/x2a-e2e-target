# Chef Deployment Role

This Ansible role deploys Chef Automate and/or Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution
- Sufficient system resources (RAM, CPU, disk space) for Chef Automate/Infra Server
- Internet connectivity to download Chef packages

## Role Variables

### Default Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_hostname | 'automate.chef.lab' | Hostname for the Chef server |
| chef_username | 'admin' | Admin username for Chef |
| chef_full_name | 'Admin User' | Full name of the admin user |
| chef_email | 'admin@example.com' | Email address for the admin user |
| chef_org_name | 'lab' | Short name for the organization |
| chef_org_full_name | 'Chef Lab' | Full name of the organization |
| deploy_automate | true | Whether to deploy Chef Automate |
| deploy_chef_server | true | Whether to deploy Chef Infra Server |
| chef_vm_max_map_count | 262144 | System parameter for Chef performance |
| chef_vm_dirty_expire_centisecs | 20000 | System parameter for Chef performance |
| chef_automate_cli_url | 'https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip' | URL to download Chef Automate CLI |
| chef_automate_cli_path | '/tmp/chef-automate' | Path to store Chef Automate CLI |
| chef_user_pem_path | '/tmp/{{ chef_username }}.pem' | Path to store user PEM file |
| chef_org_validator_pem_path | '/tmp/{{ chef_org_name }}-validator.pem' | Path to store organization validator PEM file |

### AAP Credential Variables

The following credential variables are injected by AAP credential types at runtime:

| Variable | Description |
|----------|-------------|
| username | Admin username for Chef (overrides chef_username) |
| password | Admin password for Chef |
| full_name | Full name of the admin user (overrides chef_full_name) |
| email | Email address for the admin user (overrides chef_email) |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  roles:
    - role: chef_deployment
      vars:
        chef_hostname: 'chef.example.com'
        chef_org_name: 'example'
        chef_org_full_name: 'Example Organization'
        deploy_automate: true
```

## License

Apache-2.0

## Author Information

Created by the X2A migration tool.