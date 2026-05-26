---
source-path: chef-and-ansible/tests
---

# Migration Plan: chef-inspec-tests

**TLDR**: This cookbook contains Chef InSpec tests for security compliance checking. It includes two test profiles: one for SSH security configuration and another for HTTPS website verification. These tests verify SSH root login is disabled and that a web server is properly configured with HTTPS.

## Service Type and Instances

**Service Type**: Security Compliance Tests

**Configured Instances**:
- **SSH Security Test**: Verifies SSH configuration to ensure root login is disabled
  - Location/Path: /etc/ssh/sshd_config
  - Key Config: PermitRootLogin parameter should not be set to 'yes'
  
- **HTTPS Website Test**: Verifies web server HTTPS configuration
  - Port/Socket: 443
  - Key Config: TLS 1.2 enabled, SSL3 disabled, returns 200 status code with expected content

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

The cookbook performs security compliance testing:

1. **SSH Security Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Implements a control named "Ensure_SSH_root_login_is_disabled"
   - Verifies that SSH root login is disabled in /etc/ssh/sshd_config
   - Checks that either:
     - The PermitRootLogin parameter is not set to 'yes' in sshd_config
     - OR the openssh-server package is not installed
   - Includes security metadata:
     - Security group: SRG-OS-000112
     - Vulnerability ID: V-38607
     - Rule ID: SV-50408r1_rule
     - Severity: CAT I
     - STIG ID: RHEL-08-000227
     - CCI: CCI-000774
   - Resources: sshd_config (1), package (1)

2. **HTTPS Website Test** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies that port 443 is listening
   - Tests HTTPS connection to localhost:
     - Checks for 200 status code
     - Verifies response body contains "Hello, world!"
   - Validates SSL/TLS configuration:
     - Ensures SSL3 protocol is disabled
     - Ensures TLS 1.2 protocol is enabled
   - Resources: port (1), http (1), ssl (2)

## Dependencies

**External cookbook dependencies**: None detected
**System package dependencies**: None (tests only verify existing configurations)
**Service dependencies**: SSH service, HTTPS web server

## Credentials

**Detection Summary**: 0 credentials detected across 2 files

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/ssh/sshd_config

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: localhost

**Templates rendered**: None (test-only cookbook)

## Pre-flight checks:
```bash
# SSH Configuration Check
grep PermitRootLogin /etc/ssh/sshd_config
systemctl status sshd
rpm -q openssh-server

# HTTPS Web Server Check
netstat -tulpn | grep :443
ss -tlnp | grep :443
curl -k -I https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# SSL/TLS Protocol Check
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2
```