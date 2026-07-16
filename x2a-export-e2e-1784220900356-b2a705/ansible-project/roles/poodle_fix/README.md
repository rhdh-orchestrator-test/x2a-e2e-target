# poodle_fix

This role mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured with SSL module enabled
- SSH server installed and running

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_config_path | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |
| ssl_protocol_string | -all +TLSv1.2 | SSL protocol configuration string |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
      vars:
        apache_config_path: /etc/apache2/mods-available/ssl.conf
```

## License

Apache-2.0

## Author Information

Created as part of the Chef to Ansible migration project.