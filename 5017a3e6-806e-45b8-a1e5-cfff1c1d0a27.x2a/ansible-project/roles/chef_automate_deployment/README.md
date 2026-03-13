# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on an on-premises or cloud VM.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Sufficient system resources as per Chef Automate requirements
- Internet connectivity to download Chef packages

## Role Variables

### Default Variables (can be overridden)

```yaml
# Deployment options
deploy_chef_automate: true
deploy_chef_server_only: false

# Chef Automate and Chef Infra Server configuration
hostname: 'automate.chef.lab'
username: 'jtonello'
longusername: 'John Tonello'
useremail: 'jtonello@chef.lab'
userpassword: 'password'
orgname: 'lab'
longorgname: 'Chef Lab'
```

### Generated Variables

```yaml
# Dynamic variables
userfilename: "{{ username }}.pem"
orgfilename: "{{ orgname }}-validator.pem"
```

## Dependencies

- ansible.builtin
- ansible.posix

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        hostname: 'chef.example.com'
        username: 'admin'
        longusername: 'Admin User'
        useremail: 'admin@example.com'
        userpassword: 'secure_password'
        orgname: 'myorg'
        longorgname: 'My Organization'
```

## Deploy Chef Automate Only

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        deploy_chef_automate: true
        deploy_chef_server_only: false
```

## Deploy Chef Infra Server Only

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        deploy_chef_automate: false
        deploy_chef_server_only: true
```

## License

Apache-2.0

## Author Information

Ansible Migration Team