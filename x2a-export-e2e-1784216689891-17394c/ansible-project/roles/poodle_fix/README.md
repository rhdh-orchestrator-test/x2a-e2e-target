# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured with SSL
- SSH server installed and running

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `apache_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `ssl_protocol_setting` | `-all +TLSv1.2` | SSL protocol configuration string |
| `restart_apache` | `true` | Whether to restart Apache after configuration change |
| `restart_ssh` | `true` | Whether to restart SSH after configuration change |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
      vars:
        apache_config_path: "/etc/apache2/mods-available/ssl.conf"
        ssl_protocol_setting: "-all +TLSv1.2"
```

## Security Impact

This role:
- Disables vulnerable SSL protocols (SSLv2, SSLv3, TLSv1, TLSv1.1)
- Enables only TLSv1.2 for secure communications
- Mitigates the POODLE vulnerability (CVE-2014-3566)

## License

MIT

## Author Information

Created by X2A Migration