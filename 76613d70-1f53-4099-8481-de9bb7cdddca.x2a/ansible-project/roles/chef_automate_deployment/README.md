# chef_automate_deployment

This role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Ubuntu 18.04 (bionic) or 20.04 (focal)
- Sufficient system resources as required by Chef Automate and Chef Infra Server
- Internet connectivity to download Chef Automate CLI

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| deploy_automate | true | Whether to deploy Chef Automate along with Chef Infra Server |
| deploy_chef_server | false | Whether to deploy only Chef Infra Server (without Automate) |
| chef_automate_hostname | 'automate.chef.lab' | Hostname to set on the system |
| chef_automate_username | 'jtonello' | Chef user to create |
| chef_automate_longusername | 'John Tonello' | Full name for the Chef user |
| chef_automate_useremail | 'jtonello@chef.lab' | Email for the Chef user |
| chef_automate_userpassword | 'password' | Password for the Chef user (should be overridden) |
| chef_automate_orgname | 'lab' | Chef organization name to create |
| chef_automate_longorgname | 'Chef Lab' | Full name for the Chef organization |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  roles:
    - role: chef_automate_deployment
      vars:
        chef_automate_hostname: 'chef.example.com'
        chef_automate_username: 'admin'
        chef_automate_longusername: 'Admin User'
        chef_automate_useremail: 'admin@example.com'
        chef_automate_userpassword: 'secure_password'
        chef_automate_orgname: 'example'
        chef_automate_longorgname: 'Example Organization'
```

## Post-Installation

After installation, you can access:
- Chef Automate UI at https://HOSTNAME
- Chef Infra Server API at https://HOSTNAME/organizations/ORGNAME

The following files will be created in the home directory:
- USERNAME.pem - User's private key for API access
- ORGNAME-validator.pem - Organization validator key

## License

Apache-2.0

## Author Information

This role was created as part of the Chef to Ansible migration project.