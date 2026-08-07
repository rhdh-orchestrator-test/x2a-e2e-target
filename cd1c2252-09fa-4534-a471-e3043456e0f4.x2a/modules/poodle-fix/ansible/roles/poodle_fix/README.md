# poodle_fix

This role addresses the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configurations in Apache to disable vulnerable SSL protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server must be installed
- SSH server must be installed

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ssl_config_path` | Path to Apache SSL configuration file | `/etc/apache2/mods-available/ssl.conf` |
| `ssl_protocol_string` | SSL Protocol string to use | `-all +TLSv1.2` |
| `apache_service_name` | Name of the Apache service | `apache2` |
| `ssh_service_name` | Name of the SSH service | `sshd` |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: web_servers
  roles:
    - role: poodle_fix
```

## Security Considerations

This role:
- Disables all SSL protocols except TLSv1.2
- Mitigates the POODLE vulnerability (CVE-2014-3566)
- Restarts both Apache and SSH services after configuration changes

## License

Apache-2.0

## Author Information

Created by X2A Migration Tool