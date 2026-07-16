# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and allows attackers to extract secret information from encrypted connections. This role:

- Disables vulnerable SSL protocols in Apache configuration
- Enables only TLSv1.2 for secure connections
- Restarts Apache and SSH services to apply changes

## Requirements

- Apache2 with SSL module enabled
- SSH service

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_ssl_protocol | "-all +TLSv1.2" | SSL protocol configuration for Apache |
| apache_service_name | apache2 | Name of the Apache service |
| ssh_service_name | sshd | Name of the SSH service |
| apache_ssl_conf_path | /etc/apache2/mods-available/ssl.conf | Path to Apache SSL configuration file |

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

Created by x2a migration tool.