# Poodle Fix Role

This role applies a security fix for the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

This role does not use any variables as it performs a specific security fix with hardcoded values.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
```

## Security Impact

This role makes the following security changes:

- Disables vulnerable SSL protocols in Apache configuration
- Enables only TLSv1.2 for secure connections
- Restarts Apache and SSH services to apply the changes

## License

MIT

## Author Information

Created as part of the Chef to Ansible migration project.