# SSL POODLE Remediation Role

This Ansible role mitigates the SSL POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2.

## Overview

The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and allows attackers to extract sensitive data from encrypted connections. This role helps secure your Apache web server by:

1. Updating Apache SSL configuration to disable vulnerable protocols
2. Enabling only TLSv1.2 (more secure protocol)
3. Restarting Apache and SSH services after configuration changes

## Requirements

- Apache web server installed
- SSH server installed

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssl_poodle_apache_config_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `ssl_poodle_protocol_string` | `-all +TLSv1.2` | SSL protocol string to use in Apache configuration |

## Example Playbook

```yaml
---
- hosts: webservers
  roles:
    - role: ssl_poodle_remediation
```

## Customization

You can customize the role by overriding the default variables:

```yaml
---
- hosts: webservers
  roles:
    - role: ssl_poodle_remediation
      vars:
        ssl_poodle_apache_config_path: "/path/to/custom/ssl.conf"
        ssl_poodle_protocol_string: "-all +TLSv1.2 +TLSv1.3"  # If you want to allow TLSv1.3 as well
```

## License

MIT

## Author Information

Created by the X2A migration team.