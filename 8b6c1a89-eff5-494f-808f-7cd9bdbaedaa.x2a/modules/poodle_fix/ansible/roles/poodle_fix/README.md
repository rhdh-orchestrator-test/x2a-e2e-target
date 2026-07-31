# Poodle Fix Role

This role mitigates the POODLE vulnerability in Apache SSL configuration by disabling vulnerable SSL protocols and enabling only TLSv1.2.

## Requirements

- Apache2 with SSL module enabled
- SSH server

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_ssl_conf_path | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |
| ssl_protocol | -all +TLSv1.2 | SSL protocol configuration string |
| apache_service_name | apache2 | Name of the Apache service |
| ssh_service_name | sshd | Name of the SSH service |

## Dependencies

None

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

Created by x2a