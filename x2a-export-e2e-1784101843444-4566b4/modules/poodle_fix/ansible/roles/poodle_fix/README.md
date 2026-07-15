# poodle_fix

This role implements a security fix for the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured with SSL
- SSH server installed and running

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
      vars:
        poodle_fix_apache_config_path: "/etc/httpd/conf.d/ssl.conf"  # For RHEL/CentOS
```

## License

Apache-2.0

## Author Information

Created by the X2A migration tool.