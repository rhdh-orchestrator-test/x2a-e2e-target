---
source-path: chef-and-ansible/tests
---

# Migration Plan: chef-and-ansible-tests

**TLDR**: This is a Chef InSpec test module containing two test profiles: one for SSH security configuration validation and another for HTTPS website verification. The tests check SSH root login settings and verify HTTPS website functionality including port listening, response status, content, and SSL/TLS protocol security.

## Service Type and Instances

**Service Type**: Testing/Validation Framework

**Configured Instances**:
- **SSH Security Test**: Validates SSH configuration to ensure root login is disabled
  - Target Path: /etc/ssh/sshd_config
  - Key Config: PermitRootLogin parameter should not be set to 'yes'
  
- **HTTPS Website Test**: Validates HTTPS website functionality and security
  - Port: 443
  - Expected Status: 200
  - Expected Content: "Hello, world!"
  - SSL/TLS Requirements: TLS 1.2 enabled, SSL3 disabled

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

This is not a traditional Chef cookbook with recipes, but rather a set of InSpec test profiles that would be used for validation and compliance testing. The tests perform the following operations:

1. **SSH Security Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Validates SSH configuration to ensure root login is disabled
   - Checks that either:
     - The PermitRootLogin parameter in /etc/ssh/sshd_config is not set to 'yes'
     - OR the openssh-server package is not installed
   - Includes compliance metadata:
     - Security Technical Implementation Guide (STIG) ID: RHEL-08-000227
     - Vulnerability ID: V-38607
     - CCI: CCI-000774
     - Severity: CAT I (Critical)
   - Resources: sshd_config (1), package (1)

2. **HTTPS Website Test** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies port 443 is listening
   - Checks HTTPS response:
     - Status code should be 200
     - Response body should contain "Hello, world!"
   - Validates SSL/TLS security:
     - SSL3 protocol should be disabled
     - TLS 1.2 protocol should be enabled
   - Resources: port (1), http (1), ssl (2)

## Dependencies

**External cookbook dependencies**: None detected
**System package dependencies**: None directly managed (tests check for openssh-server)
**Service dependencies**: None directly managed (tests check for HTTPS service on port 443)

## Credentials

**Detection Summary**: 0 credentials detected across 2 files

No credentials or secrets were detected in these test files. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/ssh/sshd_config (for SSH test)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: localhost (for HTTPS test)

**Templates rendered**:
No templates are rendered by these test files.

## Pre-flight checks:
```bash
# SSH Configuration Test
grep PermitRootLogin /etc/ssh/sshd_config
rpm -q openssh-server || echo "openssh-server not installed"

# HTTPS Website Test
# Check if port 443 is listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Test HTTPS response
curl -k -s -o /dev/null -w "%{http_code}" https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# Test SSL/TLS protocols
nmap --script ssl-enum-ciphers -p 443 localhost | grep -E "SSLv3|TLSv1.2"
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 disabled (expected)"
openssl s_client -connect localhost:443 -tls1_2 | grep "Protocol"
```