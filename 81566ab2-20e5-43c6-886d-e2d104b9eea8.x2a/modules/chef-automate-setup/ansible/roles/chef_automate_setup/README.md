# Chef Automate Setup Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Sufficient system resources for Chef Automate and Chef Infra Server
- Internet connectivity to download Chef Automate CLI

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_automate_hostname | 'automate.chef.lab' | Hostname for the Chef Automate server |
| chef_automate_username | 'jtonello' | Username for the Chef admin user |
| chef_automate_longusername | 'John Tonello' | Full name for the Chef admin user |
| chef_automate_useremail | 'jtonello@chef.lab' | Email for the Chef admin user |
| chef_automate_userpassword | 'password' | Password for the Chef admin user |
| chef_automate_orgname | 'lab' | Organization name for Chef |
| chef_automate_longorgname | 'Chef Lab' | Full organization name for Chef |
| chef_automate_vm_max_map_count | 262144 | Kernel parameter for vm.max_map_count |
| chef_automate_vm_dirty_expire_centisecs | 20000 | Kernel parameter for vm.dirty_expire_centisecs |
| chef_automate_deploy_with_automate | true | Whether to deploy Chef Automate with Chef Infra Server |
| chef_automate_deploy_chef_server_only | false | Whether to deploy Chef Infra Server only |

## Dependencies

- ansible.posix collection (for sysctl module)

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_setup
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_username: 'admin'
        chef_automate_userpassword: 'secure_password'
```

## License

Apache-2.0

## Author Information

Chef Migration Team