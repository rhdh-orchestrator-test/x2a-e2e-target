# Chef Server Deployment Role

This Ansible role deploys Chef Infra Server on a VM. It sets up the server, creates an initial admin user, and creates an organization.

## Requirements

- A VM with sufficient resources to run Chef Infra Server
- Internet connectivity to download Chef Automate CLI

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_server_hostname | automate.chef.lab | Hostname for the Chef Server |
| chef_server_username | jtonello | Admin username |
| chef_server_longusername | John Tonello | Admin user's full name |
| chef_server_useremail | jtonello@chef.lab | Admin user's email |
| chef_server_userpassword | password | Admin user's password |
| chef_server_orgname | lab | Organization short name |
| chef_server_longorgname | Chef Lab | Organization full name |
| chef_server_userfilename | {{ chef_server_username }}.pem | Generated admin user key filename |
| chef_server_orgfilename | {{ chef_server_orgname }}-validator.pem | Generated organization validator key filename |

## Example Playbook

```yaml
- hosts: chef_servers
  roles:
    - role: chef_server_deployment
      vars:
        chef_server_hostname: 'chef.example.com'
        chef_server_username: 'admin'
        chef_server_longusername: 'Admin User'
        chef_server_useremail: 'admin@example.com'
        chef_server_userpassword: 'secure_password'
        chef_server_orgname: 'example'
        chef_server_longorgname: 'Example Organization'
```

## License

Apache-2.0

## Author Information

Migrated from Chef Server deployment script