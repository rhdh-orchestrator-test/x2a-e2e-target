# poodle_fix

This role applies security fixes for the POODLE vulnerability by updating SSL protocol settings in Apache.

## Role Description

The POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability affects SSL 3.0 protocol. This role:

- Modifies Apache's SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure connections
- Restarts Apache and SSH services after configuration changes

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

This role does not use any variables.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: x2a.poodle_fix
```

## License

Apache-2.0