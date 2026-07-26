# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_ssl_protocol | "-all +TLSv1.2" | SSL protocol configuration for Apache |
| apache_ssl_conf_path | "/etc/apache2/mods-available/ssl.conf" | Path to Apache SSL configuration file |

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

Created as part of the Chef to Ansible migration project.