# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 protocol. This role:
- Updates Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure communications
- Restarts affected services (Apache and SSH) after configuration changes

## Requirements

- Apache2 web server installed with SSL module enabled
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ssl_protocol | "-all +TLSv1.2" | SSL protocols to enable/disable |
| apache_config_path | "/etc/apache2/mods-available/ssl.conf" | Path to Apache SSL configuration file |

## Dependencies

None

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

Created by X2A Migration Tool