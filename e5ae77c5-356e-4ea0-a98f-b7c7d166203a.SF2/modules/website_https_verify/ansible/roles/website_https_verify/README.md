# website_https_verify

This Ansible role verifies HTTPS functionality on a web server.

## Requirements

- A running web server with HTTPS enabled
- OpenSSL installed on the target system

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# HTTPS verification settings
https_host: localhost
https_port: 443
https_expected_content: "Hello, world!"
https_timeout: 10

# SSL/TLS protocol verification
ssl_protocols_disabled:
  - ssl3
ssl_protocols_enabled:
  - tls1.2
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: website_https_verify
      vars:
        https_host: "{{ inventory_hostname }}"
        https_expected_content: "Welcome to my website"
```

## Verification Tests

This role performs the following verification tests:

1. **Port verification**: Verifies that port 443 (HTTPS) is listening
2. **HTTPS content verification**: Makes an HTTPS request and verifies HTTP status code is 200 and response body contains expected content
3. **SSL protocol security verification**: Verifies that SSL3 protocol is disabled and TLS1.2 protocol is enabled

## License

Apache-2.0