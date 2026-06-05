# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on target hosts.

## Requirements

- Target system must meet Chef Automate system requirements
- Internet connectivity for downloading Chef Automate CLI
- Sufficient disk space for Chef Automate installation

## Role Variables

### Required Variables

These variables must be defined when using this role:

```yaml
username: "admin"                # Chef user username
password: "ChefPassword123!"     # Chef user password
email: "admin@example.com"       # Chef user email
full_name: "Chef Admin"          # Chef user full name
org_name: "example"              # Chef organization name
org_full_name: "Example Org"     # Chef organization full name
```

### Optional Variables

See `defaults/main.yml` for all configurable variables.

## Example Playbook

```yaml
- hosts: chef_servers
  become: true
  vars:
    username: "admin"
    password: "SecurePassword123!"
    email: "admin@example.com"
    full_name: "Chef Admin"
    org_name: "myorg"
    org_full_name: "My Organization"
  roles:
    - role: chef_automate_deployment
```

## License

Apache 2.0

## Author Information

Chef Software, Inc.