# Ansible SSL POODLE Fix Role

This role mitigates the POODLE vulnerability (CVE-2014-3566) by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ssl_config_path | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |
| ssl_protocol | "-all +TLSv1.2" | SSL protocol configuration string |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: ansible_ssl_poodle_fix_playbook
```

## Security Impact

This role makes the following security changes:

1. Disables all SSL/TLS protocols except TLSv1.2 in Apache configuration
2. Restarts Apache to apply the changes
3. Restarts SSH service

## License

Apache-2.0

## Author Information

Originally created as an Ansible playbook to mitigate the POODLE vulnerability.