# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 protocol. This role:
- Updates Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure communications
- Restarts affected services (Apache and SSH) after configuration changes

## Requirements

- Apache web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `apache_ssl_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `ssl_protocol_setting` | `-all +TLSv1.2` | SSL protocol configuration string |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

Created as part of the X2A migration project.