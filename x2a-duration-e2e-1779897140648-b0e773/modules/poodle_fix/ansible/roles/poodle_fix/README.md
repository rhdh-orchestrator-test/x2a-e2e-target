# poodle_fix

This role mitigates the POODLE vulnerability in Apache SSL configuration by updating the SSL protocol settings to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured with SSL
- SSH service installed and running

## Role Variables

No variables are defined for this role.

## Dependencies

No dependencies on other roles.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

Created as part of the Chef to Ansible migration project.