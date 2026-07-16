# poodle_fix

This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

None. This role uses fixed configurations.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## Description

The POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability affects SSLv3 and allows attackers to extract sensitive information from encrypted connections. This role mitigates the vulnerability by:

1. Updating Apache SSL configuration to disable vulnerable protocols
2. Enabling only TLSv1.2 for secure connections
3. Restarting Apache and SSH services to apply the changes

## License

Apache-2.0

## Author Information

Ansible Migration Team