# Chef Automate Deployment Role

This Ansible role deploys Chef Automate and Chef Infra Server on a target system.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Sufficient system resources:
  - At least 4 CPU cores
  - Minimum 16GB RAM
  - At least 60GB free disk space
- Internet connectivity to download Chef packages

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `deploy_chef_automate` | `true` | Deploy Chef Automate with Chef Infra Server |
| `deploy_chef_server_only` | `false` | Deploy Chef Infra Server only (without Automate) |
| `hostname` | `automate.chef.lab` | Hostname for the Chef server |
| `username` | `admin` | Admin username for Chef |
| `longusername` | `Chef Admin` | Full name for the admin user |
| `useremail` | `admin@chef.lab` | Email for the admin user |
| `userpassword` | `Ch3fAdm1n!` | Password for the admin user (should be overridden) |
| `orgname` | `chef` | Short name for the Chef organization |
| `longorgname` | `Chef Organization` | Full name for the Chef organization |

## Dependencies

- ansible.posix (for sysctl operations)

## Example Playbook

```yaml
---
- name: Deploy Chef Automate and Chef Infra Server
  hosts: chef_servers
  become: true
  vars:
    hostname: "chef.example.com"
    username: "admin"
    userpassword: "{{ vault_chef_admin_password }}"
    orgname: "example"
    longorgname: "Example Organization"
  roles:
    - role: chef_automate_deployment
```

## Alternative Example: Chef Infra Server Only

```yaml
---
- name: Deploy Chef Infra Server Only
  hosts: chef_servers
  become: true
  vars:
    deploy_chef_automate: false
    deploy_chef_server_only: true
    hostname: "chef.example.com"
  roles:
    - role: chef_automate_deployment
```

## License

Apache-2.0

## Author Information

Chef Migration Team