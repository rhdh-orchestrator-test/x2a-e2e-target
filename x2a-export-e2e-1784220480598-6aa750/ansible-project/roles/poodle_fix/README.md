# poodle_fix

An Ansible role to mitigate the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache.

## Description

This role configures Apache SSL settings to disable vulnerable SSL protocols and enable only TLSv1.2, protecting against the POODLE vulnerability (CVE-2014-3566). The POODLE vulnerability affects SSLv3 and can allow attackers to extract secret information from encrypted connections.

## Requirements

- Apache2 must be installed on the target system
- SSH service must be installed on the target system

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `apache_ssl_conf_path` | `/etc/apache2/mods-available/ssl.conf` | Path to Apache SSL configuration file |
| `ssl_protocol_string` | `-all +TLSv1.2` | SSL protocols to enable/disable |

## Dependencies

None.

## Example Playbook

```yaml
---
- hosts: webservers
  become: true
  roles:
    - role: poodle_fix
```

With custom variables:

```yaml
---
- hosts: webservers
  become: true
  roles:
    - role: poodle_fix
      vars:
        apache_ssl_conf_path: /etc/httpd/conf.d/ssl.conf
        ssl_protocol_string: "-all +TLSv1.2 +TLSv1.3"
```

## License

MIT

## Author Information

Created by the X2A migration tool.