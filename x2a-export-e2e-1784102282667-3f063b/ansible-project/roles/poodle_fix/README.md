# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and allows attackers to extract sensitive information from encrypted connections. This role:

- Updates Apache SSL configuration to disable vulnerable protocols
- Enables only TLSv1.2 for secure connections
- Restarts affected services (Apache and SSH) after configuration changes

## Requirements

- Apache2 web server installed with SSL module enabled
- SSH server installed

## Role Variables

This role does not use any variables as it applies a fixed configuration to mitigate the POODLE vulnerability.

## Dependencies

None.

## Example Playbook

```yaml
---
- hosts: webservers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

Created as part of the Chef to Ansible migration project.