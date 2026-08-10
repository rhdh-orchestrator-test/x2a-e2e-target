# poodle_fix

This role applies security fixes for the POODLE vulnerability by updating SSL/TLS protocol configurations in Apache.

## Requirements

- Apache web server installed and configured
- SSH server installed and configured

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `poodle_fix_apache_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `poodle_fix_ssl_protocol` | `-all +TLSv1.2` | SSL/TLS protocol configuration string |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## Custom Configuration

You can customize the Apache SSL configuration path and protocol settings:

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
      vars:
        poodle_fix_apache_config_path: "/path/to/custom/ssl.conf"
        poodle_fix_ssl_protocol: "-all +TLSv1.2 +TLSv1.3"
```

## License

Apache-2.0

## Author Information

Created by the X2A migration tool.