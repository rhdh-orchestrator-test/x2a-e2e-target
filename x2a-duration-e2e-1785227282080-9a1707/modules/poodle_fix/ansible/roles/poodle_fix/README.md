# Poodle Fix Role

## Description

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server must be installed
- SSH server must be installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_ssl_conf_path | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |
| apache_ssl_protocol | -all +TLSv1.2 | SSL protocol configuration string |

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

Created as part of the Chef to Ansible migration project.