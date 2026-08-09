# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| poodle_fix_ssl_protocol | -all +TLSv1.2 | SSL protocol configuration for Apache |
| poodle_fix_apache_service | apache2 | Name of the Apache service |
| poodle_fix_ssh_service | sshd | Name of the SSH service |
| poodle_fix_apache_ssl_conf | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |

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

Created by the X2A Migration Tool.