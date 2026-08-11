# Ansible Role: poodle_fix

This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed
- SSH server installed

## Role Variables

Available variables are listed below, along with default values:

```yaml
apache_config_path: "/etc/apache2/mods-available/ssl.conf"
ssl_protocol_string: "-all +TLSv1.2"
```

- `apache_config_path`: Path to Apache SSL configuration file
- `ssl_protocol_string`: SSL protocol configuration string to use in Apache config

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## License

MIT

## Author Information

This role was created as part of an Ansible migration project.