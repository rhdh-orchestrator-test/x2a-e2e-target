---
source-path: chef-and-ansible/tests
---

# Migration Plan: chef-inspec-tests

**TLDR**: This is a Chef InSpec test module containing two test files: one for SSH security configuration verification and another for HTTPS website validation. These tests check SSH root login settings and verify a web server is properly configured with HTTPS.

## Service Type and Instances

**Service Type**: Testing/Compliance Verification

**Configured Instances**:
- **SSH Security Test**: Verifies SSH configuration to ensure root login is disabled
  - Location/Path: /etc/ssh/sshd_config
  - Key Config: PermitRootLogin parameter

- **HTTPS Website Test**: Verifies HTTPS website functionality and security
  - Port/Socket: 443
  - Key Config: TLS 1.2 enabled, SSL3 disabled, website returns 200 status with expected content

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

The cookbook performs compliance testing operations:

1. **SSH Security Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Implements a control named "Ensure_SSH_root_login_is_disabled"
   - Verifies that SSH root login is disabled in /etc/ssh/sshd_config
   - Checks that either:
     - The PermitRootLogin parameter is not set to 'yes' in the SSH config
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
   - Tests HTTPS connectivity to localhost:
     - Checks for HTTP status code 200
     - Verifies response body contains "Hello, world!"
   - Validates SSL/TLS security:
     - Ensures SSL3 protocol is disabled
     - Ensures TLS 1.2 protocol is enabled
   - Resources: port (1), http (1), ssl (2)

## Dependencies

**External cookbook dependencies**: None detected
**System package dependencies**: None directly installed (tests check for openssh-server)
**Service dependencies**: Web server with HTTPS enabled

## Credentials

**Detection Summary**: 0 credentials detected across 2 files

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/ssh/sshd_config (for SSH test)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: localhost (for HTTPS test)

**Templates rendered**:
None detected - these are test files only, not configuration templates

## Pre-flight checks:
```bash
# SSH Configuration Test
# Check if SSH root login is disabled
grep -i "PermitRootLogin" /etc/ssh/sshd_config
# Check if openssh-server is installed
rpm -q openssh-server || dpkg -l | grep openssh-server

# HTTPS Website Test
# Check if port 443 is listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Test HTTPS connectivity
curl -k -I https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# Test SSL/TLS protocols
nmap --script ssl-enum-ciphers -p 443 localhost | grep -E "SSLv3|TLSv1.2"
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2 | grep "Protocol"
```