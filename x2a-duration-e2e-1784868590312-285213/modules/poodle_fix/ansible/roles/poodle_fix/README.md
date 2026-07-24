# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `apache_ssl_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `ssl_protocol_setting` | `-all +TLSv1.2` | SSL protocol configuration string for Apache |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## Advanced Usage

You can customize the SSL configuration path and protocol settings:

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
      vars:
        apache_ssl_config_path: "/custom/path/to/ssl.conf"
        ssl_protocol_setting: "-all +TLSv1.2 +TLSv1.3"
```

## License

Apache-2.0

## Author Information

Created by X2A Migration Tool