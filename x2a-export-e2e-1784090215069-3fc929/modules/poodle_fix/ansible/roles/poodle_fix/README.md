# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

This role does not use any variables as it performs a specific security fix with hardcoded values.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## Security Impact

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability (CVE-2014-3566) by:

- Disabling all SSL protocols except TLSv1.2 in Apache's SSL configuration
- Restarting Apache and SSH services to apply the changes

## License

Apache-2.0

## Author Information

Created by the X2A migration tool.