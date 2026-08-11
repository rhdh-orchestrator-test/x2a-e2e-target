# Poodle Fix Role

This role implements a security fix for the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured with SSL
- SSH server installed and running

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_config_path | "/etc/apache2/mods-available/ssl.conf" | Path to Apache SSL configuration file |
| ssl_protocol_setting | "SSLProtocol -all +TLSv1.2" | SSL protocol configuration string |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: poodle_fix
      vars:
        apache_config_path: "/etc/httpd/conf.d/ssl.conf"  # For RHEL/CentOS
```

## Security Impact

This role mitigates the POODLE vulnerability (CVE-2014-3566) by:
- Disabling vulnerable SSL protocols (SSLv2, SSLv3, TLSv1, TLSv1.1)
- Enabling only TLSv1.2 which is not vulnerable to POODLE

## License

Apache-2.0

## Author Information

Created by x2a migration tool.