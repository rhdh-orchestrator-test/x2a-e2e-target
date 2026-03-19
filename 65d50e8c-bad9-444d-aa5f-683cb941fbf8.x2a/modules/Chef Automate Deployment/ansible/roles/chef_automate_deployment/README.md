# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Target system must be a supported Linux distribution (Ubuntu 18.04/20.04 recommended)
- Sufficient system resources (minimum 4GB RAM, 2 CPUs, 40GB disk space)
- Internet connectivity to download Chef packages
- Sudo/root access on the target system

## Role Variables

All variables are defined in `defaults/main.yml` and can be overridden:

```yaml
# Deployment type: "full", "both", "infra-server", or "chef-server"
chef_automate_deploy_type: "full"

# Chef Automate and Chef Infra Server configuration
chef_automate_hostname: 'automate.chef.lab'
chef_automate_username: 'jtonello'
chef_automate_longusername: 'John Tonello'
chef_automate_useremail: 'jtonello@chef.lab'
chef_automate_userpassword: 'password'
chef_automate_orgname: 'lab'
chef_automate_longorgname: 'Chef Lab'

# Derived variables - do not change
chef_automate_userfilename: "{{ chef_automate_username }}.pem"
chef_automate_orgfilename: "{{ chef_automate_orgname }}-validator.pem"

# System configuration
chef_automate_vm_max_map_count: 262144
chef_automate_vm_dirty_expire_centisecs: 20000
```

## Dependencies

- ansible.posix collection (for sysctl module)

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_deploy_type: "full"  # Deploy both Chef Automate and Chef Infra Server
        chef_automate_hostname: 'chef.example.com'
        chef_automate_username: 'admin'
        chef_automate_userpassword: 'secure_password'
```

For deploying only Chef Infra Server:

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_deploy_type: "infra-server"  # Deploy only Chef Infra Server
```

## Post-Installation

After deployment:

1. Access Chef Automate UI at `https://<chef_automate_hostname>`
2. Access Chef Infra Server UI at `https://<chef_automate_hostname>/organizations/<chef_automate_orgname>`
3. User key file will be saved as `<chef_automate_username>.pem`
4. Organization validator key will be saved as `<chef_automate_orgname>-validator.pem`

## License

Apache-2.0