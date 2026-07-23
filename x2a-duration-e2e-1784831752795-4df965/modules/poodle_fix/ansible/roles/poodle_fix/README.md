# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 protocol. This role updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2, which is not affected by this vulnerability.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_config_path | "/etc/apache2/mods-available/ssl.conf" | Path to Apache SSL configuration file |
| ssl_protocol_setting | "-all +TLSv1.2" | SSL protocol configuration string |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
```

With custom variables:

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
      vars:
        apache_config_path: "/custom/path/to/ssl.conf"
        ssl_protocol_setting: "-all +TLSv1.2 +TLSv1.3"
```

## License

MIT

## Author Information

Created by X2A Migration Tool