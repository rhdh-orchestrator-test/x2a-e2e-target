# chef_inspec_tests

This Ansible role contains security and functionality tests migrated from Chef InSpec tests.

## Tests Included

### SSH Security Tests

Tests SSH configuration to ensure root login is disabled:
- Checks that PermitRootLogin is not set to 'yes' in /etc/ssh/sshd_config
- Alternative check: Verifies openssh-server package is not installed
- Security tags: SRG-OS-000112, V-38607, SV-50408r1_rule, CAT I, RHEL-08-000227, CCI-000774

### HTTPS Website Tests

Verifies HTTPS website functionality and security:
- Tests that port 443 is listening
- Checks that HTTPS request to localhost returns 200 status code
- Validates that response body contains "Hello, world!" text
- Ensures insecure SSL3 protocol is disabled
- Confirms secure TLS 1.2 protocol is enabled

## Requirements

- Ansible 2.9 or higher
- Target system with SSH configuration (for SSH tests)
- Target system with web server configured for HTTPS (for website tests)

## Role Variables

All variables are defined in `defaults/main.yml` and can be overridden:

```yaml
# SSH Security Test variables
ssh_config_path: /etc/ssh/sshd_config
ssh_package_name: openssh-server

# HTTPS Website Test variables
https_port: 443
https_url: https://localhost/
https_expected_content: "Hello, world!"
https_expected_status_code: 200

# SSL/TLS Protocol Test variables
ssl_tls_protocols:
  ssl3: false  # Should be disabled
  tls1.2: true  # Should be enabled
```

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: chef_inspec_tests
```

## License

Apache-2.0