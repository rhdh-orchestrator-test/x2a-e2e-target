# poodle_fix

This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| poodle_fix_ssl_protocol | "-all +TLSv1.2" | SSL protocol configuration for Apache |
| apache_service_name | apache2 | Name of the Apache service |
| ssh_service_name | sshd | Name of the SSH service |
| apache_ssl_conf_path | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: web_servers
  roles:
    - role: poodle_fix
```

## Security Considerations

This role addresses the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability (CVE-2014-3566) by:

1. Disabling all SSL protocols in Apache
2. Enabling only TLSv1.2, which is not vulnerable to POODLE
3. Restarting Apache and SSH services to apply the changes

## License

Apache-2.0

## Author Information

Created by X2A Migration Tool