# Poodle Fix Role

This role mitigates the POODLE vulnerability (CVE-2014-3566) by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

None

## Dependencies

None

## Example Playbook

```yaml
- hosts: servers
  roles:
    - poodle_fix
```

## License

MIT

## Author Information

Ansible to Ansible Migration