# poodle_fix

An Ansible role to mitigate the POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability in Apache web servers.

## Description

This role implements a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The POODLE vulnerability (CVE-2014-3566) affects SSLv3 and can allow attackers to extract sensitive data from encrypted connections.

## Requirements

- Apache2 web server installed
- SSH server installed

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Path to Apache SSL configuration file
apache_ssl_config_path: /etc/apache2/mods-available/ssl.conf

# SSL protocol setting to mitigate POODLE vulnerability
ssl_protocol_setting: 'SSLProtocol -all +TLSv1.2'
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

Created by the X2A migration tool.