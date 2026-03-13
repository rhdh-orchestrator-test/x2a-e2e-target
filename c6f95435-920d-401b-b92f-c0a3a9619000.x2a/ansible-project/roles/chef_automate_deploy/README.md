# chef_automate_deploy

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Sufficient system resources:
  - At least 4 CPU cores
  - At least 16GB RAM
  - At least 60GB free disk space
- Internet connectivity to download Chef packages

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| chef_automate_deploy_full | true | Whether to deploy full Chef Automate with Infra Server (true) or just Chef Infra Server (false) |
| chef_automate_hostname | 'automate.chef.lab' | Hostname to set on the target system |
| chef_automate_username | 'jtonello' | Admin username to create |
| chef_automate_longusername | 'John Tonello' | Full name of the admin user |
| chef_automate_useremail | 'jtonello@chef.lab' | Email address of the admin user |
| chef_automate_userpassword | 'password' | Password for the admin user (should be overridden) |
| chef_automate_orgname | 'lab' | Short name of the organization to create |
| chef_automate_longorgname | 'Chef Lab' | Full name of the organization |
| chef_automate_userfilename | "{{ chef_automate_username }}.pem" | Filename for the user key (auto-generated) |
| chef_automate_orgfilename | "{{ chef_automate_orgname }}-validator.pem" | Filename for the organization validator key (auto-generated) |

## Dependencies

- ansible.builtin
- ansible.posix

## Example Playbook

```yaml
---
- name: Deploy Chef Automate and Chef Infra Server
  hosts: chef_servers
  become: true
  vars:
    chef_automate_hostname: 'chef.example.com'
    chef_automate_username: 'admin'
    chef_automate_longusername: 'Admin User'
    chef_automate_useremail: 'admin@example.com'
    chef_automate_userpassword: 'secure_password'
    chef_automate_orgname: 'example'
    chef_automate_longorgname: 'Example Organization'
  roles:
    - role: chef_automate_deploy
```

## License

Apache-2.0

## Author Information

Chef Migration Team