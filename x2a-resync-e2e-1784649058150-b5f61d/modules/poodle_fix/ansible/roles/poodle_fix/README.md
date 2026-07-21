# poodle_fix

This role mitigates the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache SSL configuration.

## Description

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 protocol. This role:

- Updates Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure communications
- Restarts Apache and SSH services after configuration changes

## Requirements

- Apache web server installed with SSL module enabled
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `apache_ssl_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `ssl_protocol_setting` | `-all +TLSv1.2` | SSL protocol configuration string |
| `restart_apache` | `true` | Whether to restart Apache after configuration changes |
| `restart_ssh` | `true` | Whether to restart SSH after configuration changes |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: poodle_fix
      vars:
        apache_ssl_config_path: "/etc/apache2/mods-available/ssl.conf"
        ssl_protocol_setting: "-all +TLSv1.2"
```

## Verification

After applying this role, you can verify the POODLE vulnerability is mitigated:

```bash
# Check Apache configuration
apache2ctl configtest

# Test SSL connection with TLSv1.2
openssl s_client -connect localhost:443 -tls1_2

# Verify POODLE vulnerability is mitigated
nmap --script ssl-enum-ciphers -p 443 localhost
```

## License

Apache-2.0

## Author Information

Created by X2A Migration Tool