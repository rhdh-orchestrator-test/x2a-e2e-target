# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and allows attackers to extract sensitive information from encrypted connections. This role:

- Updates Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure connections
- Restarts affected services (Apache and SSH) after configuration changes

## Requirements

- Apache web server with SSL module enabled
- SSH server

## Role Variables

None. This role uses fixed configurations to enforce security best practices.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

Created by the X2A migration tool.