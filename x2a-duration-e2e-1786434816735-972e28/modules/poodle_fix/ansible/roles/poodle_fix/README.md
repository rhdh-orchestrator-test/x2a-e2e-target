# Poodle Fix

An Ansible role to mitigate the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and can allow attackers to extract sensitive data from encrypted connections.

## Requirements

- Apache2 web server installed with SSL module enabled
- SSH server installed

## Role Variables

This role does not use any variables as it applies a specific security fix with hardcoded values.

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

- Disables SSLv3 and other vulnerable protocols in Apache
- Enables only TLSv1.2 for secure connections
- Restarts Apache and SSH services to apply changes

## License

MIT

## Author Information

Created by the X2A migration tool.