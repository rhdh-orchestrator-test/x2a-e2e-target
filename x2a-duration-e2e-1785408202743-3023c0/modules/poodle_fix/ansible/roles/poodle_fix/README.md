# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssl_protocol` | `-all +TLSv1.2` | SSL protocols to enable/disable |
| `apache_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `restart_services` | `true` | Whether to restart services after configuration changes |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
      vars:
        ssl_protocol: "-all +TLSv1.2"
```

## License

MIT

## Author Information

Created by the X2A migration tool.