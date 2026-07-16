# poodle_fix

This role mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured with SSL
- SSH server installed and running

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssl_protocols` | `-all +TLSv1.2` | SSL protocols to enable/disable in Apache |
| `apache_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## License

Apache-2.0

## Author Information

Created by the X2A migration tool.