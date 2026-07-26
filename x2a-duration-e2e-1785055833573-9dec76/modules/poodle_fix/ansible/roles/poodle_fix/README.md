# Ansible Role: poodle_fix

This role applies security fixes for the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured with SSL
- SSH server installed and running

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Apache SSL configuration
poodle_fix_apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf
poodle_fix_ssl_protocol: '-all +TLSv1.2'

# Service names - can be overridden for different distributions
poodle_fix_apache_service_name: apache2
poodle_fix_ssh_service_name: sshd

# Backup and validation settings
poodle_fix_create_backup: true
poodle_fix_validate_config: true
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
```

## License

Apache-2.0

## Author Information

This role was created as part of an automated migration from legacy infrastructure code.

## Security Notes

This role specifically addresses the POODLE vulnerability (CVE-2014-3566) by:

1. Disabling all SSL protocols
2. Enabling only TLSv1.2 (considered secure at the time of writing)

For more comprehensive security hardening, consider:
- Enabling TLSv1.3 where supported
- Configuring secure cipher suites
- Implementing HTTP Strict Transport Security (HSTS)
- Regular security audits and updates