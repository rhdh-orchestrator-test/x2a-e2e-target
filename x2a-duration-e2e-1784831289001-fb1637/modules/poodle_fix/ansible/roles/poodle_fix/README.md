# Poodle Fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and allows attackers to extract sensitive information from encrypted connections. This role updates the Apache SSL configuration to disable vulnerable protocols and enable only TLSv1.2, which is not affected by this vulnerability.

## Requirements

- Apache2 with SSL module enabled
- SSH server

## Role Variables

This role does not use any variables.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
```

## Actions Performed

1. Updates Apache SSL configuration to disable vulnerable SSL protocols
2. Enables only TLSv1.2 in the Apache SSL configuration
3. Restarts Apache and SSH services after configuration changes

## License

MIT

## Author Information

Created by X2A Migration Tool