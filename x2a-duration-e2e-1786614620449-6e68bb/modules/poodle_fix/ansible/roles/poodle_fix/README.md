# poodle_fix

This role mitigates the POODLE vulnerability by updating SSL configurations in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_ssl_config_path | "/etc/apache2/mods-available/ssl.conf" | Path to Apache SSL configuration file |
| ssl_protocol_setting | "-all +TLSv1.2" | SSL protocol configuration string for Apache |

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