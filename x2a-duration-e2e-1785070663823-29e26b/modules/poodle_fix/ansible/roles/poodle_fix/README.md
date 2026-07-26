# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and allows attackers to extract secret information from encrypted connections. This role:

- Updates Apache SSL configuration to disable vulnerable protocols
- Enables only TLSv1.2 to mitigate the vulnerability
- Restarts affected services after configuration changes

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_ssl_conf_path | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |
| ssl_protocol_setting | -all +TLSv1.2 | SSL protocol configuration string |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
```

## License

Apache-2.0

## Author Information

Created by X2A Migration Tool