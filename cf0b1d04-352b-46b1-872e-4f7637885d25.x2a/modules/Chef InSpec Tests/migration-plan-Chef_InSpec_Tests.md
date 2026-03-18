# Migration Plan: Chef InSpec Tests

**TLDR**: This module contains Chef InSpec tests for SSH security configuration and HTTPS website verification. It includes two test files: one for validating SSH root login is disabled and another for verifying HTTPS website functionality, including port listening, response status, content validation, and SSL/TLS protocol security.

## Service Type and Instances

**Service Type**: Testing Framework (InSpec)

**Configured Tests**:

- **SSH Security Test**: 
  - Location/Path: chef-and-ansible/tests/ssh_profile.rb
  - Key Config: Verifies SSH root login is disabled in /etc/ssh/sshd_config
  - Security Tags: SRG-OS-000112, V-38607, SV-50408r1_rule, CAT I, RHEL-08-000227, CCI-000774

- **HTTPS Website Test**:
  - Location/Path: chef-and-ansible/tests/website_https_verify.rb
  - Port/Socket: 443
  - Key Config: Verifies HTTPS port is listening, website returns 200 status code, contains "Hello, world!" text, and uses secure TLS protocols

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

The Chef InSpec test module performs the following tests:

1. **SSH Security Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Tests SSH configuration to ensure root login is disabled
   - Implements a control named "Ensure_SSH_root_login_is_disabled"
   - Provides detailed security rationale and documentation
   - Includes security tags for compliance tracking (SRG-OS-000112, V-38607, etc.)
   - Uses two alternative test conditions:
     - Checks that PermitRootLogin is not set to 'yes' in /etc/ssh/sshd_config
     - OR checks that openssh-server package is not installed
   - Resources: sshd_config (1), package (1)

2. **HTTPS Website Test** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies HTTPS website functionality and security
   - Tests that port 443 is listening
   - Checks that HTTPS request to localhost returns 200 status code
   - Validates that response body contains "Hello, world!" text
   - Ensures insecure SSL3 protocol is disabled
   - Confirms secure TLS 1.2 protocol is enabled
   - Resources: port (1), http (1), ssl (2)

## Dependencies

**External dependencies**: None specified in the files
**System package dependencies**: None explicitly required, but tests check for openssh-server
**Service dependencies**: Web server with HTTPS enabled

## Checks for the Migration

**Files to verify**:
- /etc/ssh/sshd_config (for SSH test)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: localhost

**Tests to implement**:
- SSH root login configuration test
- HTTPS port listening test
- HTTPS response status code test
- HTTPS response content test
- SSL/TLS protocol security tests

## Pre-flight checks:

```bash
# SSH Configuration Test
# Check if openssh-server is installed
rpm -q openssh-server || dpkg -l | grep openssh-server

# Check SSH root login configuration
grep -i "PermitRootLogin" /etc/ssh/sshd_config

# HTTPS Website Test
# Check if port 443 is listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Test HTTPS response
curl -k -I https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# Check SSL/TLS protocols
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2 | grep "Protocol"
```