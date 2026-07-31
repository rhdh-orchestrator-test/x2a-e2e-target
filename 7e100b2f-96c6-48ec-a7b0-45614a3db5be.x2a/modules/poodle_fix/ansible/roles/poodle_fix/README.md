# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

No variables are defined in this role.

## Dependencies

No dependencies on other roles.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## License

Apache-2.0

## Author Information

Originally created for Chef and Ansible migration project.