# website_https_verify

An Ansible role to verify HTTPS functionality on a web server.

## Description

This role provides tests to verify that a web server is properly configured for HTTPS:

- Verifies that port 443 (HTTPS) is listening
- Makes an HTTPS request to localhost and verifies:
  - HTTP status code is 200
  - Response body contains "Hello, world!"
- Verifies SSL/TLS protocol security:
  - Insecure SSL3 protocol is disabled
  - Secure TLS 1.2 protocol is enabled

## Requirements

- A web server with HTTPS enabled
- OpenSSL command-line tools

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Whether to run the verification tests
run_tests: false

# HTTPS verification settings
https_port: 443
https_host: localhost
https_expected_content: "Hello, world!"

# SSL/TLS protocol settings to verify
ssl3_should_be_enabled: false
tls1_2_should_be_enabled: true
```

## Dependencies

None.

## Example Playbook

```yaml
---
- hosts: webservers
  roles:
    - role: website_https_verify
      vars:
        run_tests: true
```

## Pre-flight Checks

You can manually verify the HTTPS configuration with these commands:

```bash
# Port verification
ss -tlnp | grep :443
netstat -tulpn | grep :443

# Web server status
systemctl status apache2  # Or nginx, depending on the web server

# HTTPS content verification
curl -k https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2 | grep "Protocol"

# Certificate verification
openssl s_client -connect localhost:443 | openssl x509 -noout -text
```

## License

Apache-2.0