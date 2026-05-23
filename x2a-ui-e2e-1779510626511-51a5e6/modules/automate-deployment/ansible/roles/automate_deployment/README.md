# automate_deployment

This role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system should have at least 8GB RAM and 40GB disk space
- Internet connectivity to download Chef Automate CLI
- Sudo/root access on the target system

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| automate_hostname | Hostname to set for the Chef Automate server | automate.chef.lab |
| automate_cli_url | URL to download Chef Automate CLI | https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip |
| automate_cli_path | Path to store the Chef Automate CLI | ./chef-automate |
| automate_vm_max_map_count | Kernel parameter vm.max_map_count | 262144 |
| automate_vm_dirty_expire_centisecs | Kernel parameter vm.dirty_expire_centisecs | 20000 |
| automate_accept_terms_and_mlsa | Whether to accept Chef's terms and MLSA | true |
| automate_username | Chef user username | From AAP credentials or jtonello |
| automate_full_name | Chef user full name | From AAP credentials or John Tonello |
| automate_email | Chef user email | From AAP credentials or jtonello@chef.lab |
| automate_password | Chef user password | From AAP credentials or password |
| automate_org_name | Chef organization short name | lab |
| automate_org_full_name | Chef organization full name | Chef Lab |
| automate_user_pem_file | Path to save user PEM file | {{ automate_username }}.pem |
| automate_org_validator_pem | Path to save organization validator PEM file | {{ automate_org_name }}-validator.pem |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: automate_deployment
      vars:
        automate_hostname: 'chef.example.com'
        automate_org_name: 'example'
        automate_org_full_name: 'Example Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef scripts to Ansible role.