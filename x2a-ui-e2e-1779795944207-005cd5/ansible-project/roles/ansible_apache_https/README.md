# Ansible Apache HTTPS Role

This role configures an Apache web server with HTTPS support using a self-signed certificate.

## Requirements

- Ubuntu 18.04 (Bionic) or Ubuntu 20.04 (Focal)
- Ansible 2.9 or higher

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| apache_version | 2.4.41-4ubuntu3.10 | Apache version to install |
| website_domain | myhost | Domain name for the website |
| website_root | /var/www/helloworld | Website document root |
| ssl_cert_dir | /etc/apache2/certs | Directory for SSL certificates |
| ssl_key_path | /etc/apache2/certs/apache.key | Path to SSL key |
| ssl_csr_path | /etc/apache2/certs/apache.csr | Path to SSL CSR |
| ssl_cert_path | /etc/apache2/certs/apache.crt | Path to SSL certificate |

## Dependencies

None

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: ansible_apache_https
      website_domain: example.com
      website_root: /var/www/example
```

## License

MIT

## Author Information

Ansible Migration Team