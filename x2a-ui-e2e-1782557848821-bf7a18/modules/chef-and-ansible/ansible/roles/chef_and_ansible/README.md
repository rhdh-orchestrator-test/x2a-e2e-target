# chef_and_ansible

This role sets up a secure Apache web server with SSL/TLS.

## Requirements

- Ubuntu 20.04 (Focal)
- Ansible 2.9 or higher

## Role Variables

- `conftext`: The Apache virtual host configuration
- `webtext`: The HTML content for the website

## Dependencies

None

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: x2a.chef_and_ansible
```

## License

MIT

## Author Information

Ansible Migration Team