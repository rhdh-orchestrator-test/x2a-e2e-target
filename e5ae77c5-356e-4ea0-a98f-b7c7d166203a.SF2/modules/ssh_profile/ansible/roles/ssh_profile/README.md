# SSH Profile

This Ansible role performs security compliance checks for SSH configuration.

## Security Compliance Information

- **STIG ID**: RHEL-08-000227
- **Vulnerability ID**: V-38607
- **Rule ID**: SV-50408r1_rule
- **Category**: CAT I (highest severity)
- **CCI**: CCI-000774

## Requirements

- Ansible 2.9 or higher

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# SSH configuration file path
ssh_config_path: /etc/ssh/sshd_config

# Security compliance settings
ssh_permit_root_login: "no"
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: ssh_profile
```

## Usage

This role can be used to check SSH security compliance:

```bash
# Run with check mode to only report issues without making changes
ansible-playbook -i inventory playbook.yml --check --tags security

# Run compliance check and see detailed output
ansible-playbook -i inventory playbook.yml -v --tags security
```

## License

Apache-2.0

## Author Information

Ansible Migration Team