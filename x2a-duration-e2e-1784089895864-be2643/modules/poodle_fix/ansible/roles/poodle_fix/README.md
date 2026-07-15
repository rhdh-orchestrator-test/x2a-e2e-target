# poodle_fix

This role addresses the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Requirements

- Apache web server installed and configured
- SSH server installed and configured

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_ssl_config_path | '/etc/apache2/mods-available/ssl.conf' | Path to Apache SSL configuration file |
| ssl_protocol_setting | '-all +TLSv1.2' | SSL protocol settings for Apache |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
```

## Security Impact

This role improves security by:
- Disabling vulnerable SSL protocols (SSLv2, SSLv3, TLSv1, TLSv1.1)
- Enabling only TLSv1.2, which is not vulnerable to POODLE attacks
- Restarting affected services to apply the changes

## License

Apache-2.0

## Author Information

Created by the X2A migration tool.