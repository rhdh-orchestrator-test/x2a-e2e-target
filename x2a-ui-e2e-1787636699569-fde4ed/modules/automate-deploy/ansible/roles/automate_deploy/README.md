# automate_deploy

This role deploys Chef Automate and Chef Infra Server on a Linux system.

## Requirements

- Target system must be a supported Linux distribution (RHEL/CentOS 7+, Ubuntu 18.04+)
- Minimum system requirements:
  - 4 CPU cores
  - 16GB RAM
  - 60GB free disk space
- Internet connectivity to download Chef Automate CLI
- Sudo/root access

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `automate_deploy_hostname` | 'automate.chef.lab' | Hostname to set for the Chef Automate server |
| `automate_deploy_kernel_params` | See defaults/main.yml | Kernel parameters required for Chef Automate |
| `automate_deploy_cli_url` | "https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip" | URL to download the Chef Automate CLI |
| `automate_deploy_cli_path` | "/tmp/chef-automate" | Path where the Chef Automate CLI will be saved |
| `automate_deploy_user_pem_path` | "/tmp/{{ username }}.pem" | Path where the user PEM file will be saved |
| `automate_deploy_org_validator_pem_path` | "/tmp/{{ org_name }}-validator.pem" | Path where the organization validator PEM file will be saved |

## AAP Credential Variables

This role requires the following credential variables to be provided by AAP:

| Variable | Description |
|----------|-------------|
| `username` | Username for the Chef admin user |
| `long_username` | Full name for the Chef admin user |
| `user_email` | Email address for the Chef admin user |
| `user_password` | Password for the Chef admin user |
| `org_name` | Short name for the Chef organization |
| `long_org_name` | Full name for the Chef organization |

## Dependencies

None.

## Example Playbook

```yaml
- name: Deploy Chef Automate and Chef Infra Server
  hosts: chef_servers
  become: true
  roles:
    - role: automate_deploy
      vars:
        automate_deploy_hostname: 'chef.example.com'
```

## License

Apache-2.0

## Author Information

Migrated from Chef deployment script by X2A Migration Tool.