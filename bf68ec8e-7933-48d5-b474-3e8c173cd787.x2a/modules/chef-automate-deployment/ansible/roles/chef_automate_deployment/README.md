# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on an on-prem or cloud VM.

## Requirements

- Ubuntu 18.04 (bionic) or 20.04 (focal)
- Sufficient system resources for Chef Automate and Chef Infra Server
- Internet connectivity to download Chef Automate CLI

## Role Variables

### Default Variables (can be overridden)

```yaml
# System configuration
vm_max_map_count: 262144
vm_dirty_expire_centisecs: 20000

# Chef Automate CLI download URL
chef_automate_cli_url: "https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip"

# Deployment options
accept_terms_and_mlsa: true
```

### Required Variables (defined in vars/main.yml, can be overridden)

```yaml
# Variables for Chef Automate and Chef Infra Server deployment
hostname: 'automate.chef.lab'
username: 'jtonello'
longusername: 'John Tonello'
useremail: 'jtonello@chef.lab'
userpassword: 'password'
orgname: 'lab'
longorgname: 'Chef Lab'

# Dynamic variables
userfilename: "{{ username }}.pem"
orgfilename: "{{ orgname }}-validator.pem"
```

## Dependencies

- ansible.posix collection (for sysctl module)
- community.general collection

## Example Playbook

### Deploy Chef Automate and Chef Infra Server

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        deployment_type: 'full'  # Optional, defaults to 'full'
```

### Deploy Chef Infra Server Only

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        deployment_type: 'infra-server-only'
```

## License

Apache-2.0

## Author Information

This role was created as part of the Chef to Ansible migration project.