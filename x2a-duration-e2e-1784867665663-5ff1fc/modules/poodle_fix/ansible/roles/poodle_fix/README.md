# poodle_fix

This role mitigates the POODLE SSL vulnerability in Apache by updating the SSL configuration to disable vulnerable protocols and enable only secure TLS versions.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssl_protocols` | `-all +TLSv1.2` | SSL/TLS protocols to enable/disable in Apache configuration |
| `apache_ssl_conf_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## Advanced Usage

You can customize the SSL protocols by overriding the default variables:

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
      vars:
        ssl_protocols: "-all +TLSv1.2 +TLSv1.3"
```

## License

MIT

## Author Information

Created by X2A Migration Tool