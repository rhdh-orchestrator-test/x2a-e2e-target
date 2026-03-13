# Chef Automate Setup Role

This Ansible role automates the deployment of Chef Automate and Chef Infra Server on an on-premises or cloud VM.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Sufficient system resources as per Chef Automate requirements
- Internet connectivity to download Chef Automate CLI

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_automate_hostname | 'automate.chef.lab' | Hostname for the Chef Automate server |
| chef_automate_username | 'jtonello' | Username for the initial Chef user |
| chef_automate_longusername | 'John Tonello' | Full name for the initial Chef user |
| chef_automate_useremail | 'jtonello@chef.lab' | Email for the initial Chef user |
| chef_automate_userpassword | 'password' | Password for the initial Chef user |
| chef_automate_orgname | 'lab' | Short name for the Chef organization |
| chef_automate_longorgname | 'Chef Lab' | Full name for the Chef organization |
| chef_automate_vm_max_map_count | 262144 | Kernel parameter for vm.max_map_count |
| chef_automate_vm_dirty_expire_centisecs | 20000 | Kernel parameter for vm.dirty_expire_centisecs |
| chef_install_automate | true | Whether to install Chef Automate with Infra Server |
| chef_install_server_only | false | Whether to install Chef Infra Server only (without Automate) |

## Dependencies

- ansible.posix collection
- community.general collection

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

Chef to Ansible Migration Project