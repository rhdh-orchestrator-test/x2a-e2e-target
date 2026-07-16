# poodle_fix

This role implements a security fix for the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssl_protocol` | `-all +TLSv1.2` | SSL/TLS protocols to enable/disable in Apache |
| `apache_ssl_conf_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

Created as part of the Chef to Ansible migration project.