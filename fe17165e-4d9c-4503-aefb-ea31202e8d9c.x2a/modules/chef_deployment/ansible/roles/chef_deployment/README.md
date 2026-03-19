# Chef Deployment Role

This Ansible role automates the deployment of Chef Automate and Chef Infra Server.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Ansible 2.9 or higher
- `ansible.posix` collection for sysctl module

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| hostname | 'automate.chef.lab' | Hostname for the Chef server |
| username | 'jtonello' | Chef user's username |
| longusername | 'John Tonello' | Chef user's full name |
| useremail | 'jtonello@chef.lab' | Chef user's email |
| userpassword | 'password' | Chef user's password |
| orgname | 'lab' | Chef organization short name |
| longorgname | 'Chef Lab' | Chef organization full name |
| deploy_automate | true | Deploy Chef Automate with Infra Server |
| deploy_chef_server | false | Deploy Chef Infra Server only |

## Dependencies

- ansible.posix collection

## Example Playbook

```yaml
---
- hosts: chef_servers
  become: true
  roles:
    - role: chef_deployment
      vars:
        hostname: 'chef.example.com'
        username: 'admin'
        longusername: 'Admin User'
        useremail: 'admin@example.com'
        userpassword: 'secure_password'
        orgname: 'myorg'
        longorgname: 'My Organization'
```

## Deployment Options

### Deploy Chef Automate with Infra Server

This is the default behavior. The role will deploy both Chef Automate and Chef Infra Server.

```yaml
- hosts: chef_servers
  roles:
    - role: chef_deployment
      vars:
        deploy_automate: true
        deploy_chef_server: false  # Not needed as it's the default
```

### Deploy Chef Infra Server Only

To deploy only Chef Infra Server without Chef Automate:

```yaml
- hosts: chef_servers
  roles:
    - role: chef_deployment
      vars:
        deploy_automate: false
        deploy_chef_server: true
```

## License

Apache-2.0

## Author Information

Chef Migration Team