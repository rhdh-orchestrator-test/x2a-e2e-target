# Migration Plan: Chef InSpec Tests

**TLDR**: This module contains Chef InSpec tests for SSH security configuration and HTTPS website verification. It includes two test files: one for validating SSH root login is disabled and another for verifying HTTPS website functionality, including port listening, response status, content validation, and SSL/TLS protocol security.

## Service Type and Instances

**Service Type**: Testing Framework (InSpec)

**Configured Tests**:

- **SSH Security Test**: Validates SSH configuration security
  - Location/Path: chef-and-ansible/tests/ssh_profile.rb
  - Key Config: Checks that PermitRootLogin is not set to 'yes' in /etc/ssh/sshd_config

- **HTTPS Website Test**: Validates website availability and security
  - Location/Path: chef-and-ansible/tests/website_https_verify.rb
  - Port/Socket: 443
  - Key Config: Verifies port 443 is listening, website returns 200 status code, content contains "Hello, world!", SSL3 is disabled, and TLS1.2 is enabled

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

The Chef InSpec test module performs the following validations:

1. **SSH Security Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Validates that SSH root login is disabled for security compliance
   - Uses InSpec's sshd_config resource to check the PermitRootLogin setting in /etc/ssh/sshd_config
   - Alternatively checks if openssh-server package is not installed
   - Includes compliance metadata:
     - Security group: SRG-OS-000112
     - Vulnerability ID: V-38607
     - Rule ID: SV-50408r1_rule
     - Severity: CAT I
     - STIG ID: RHEL-08-000227
     - CCI: CCI-000774
   - Resources: sshd_config (1), package (1)

2. **HTTPS Website Test** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Validates that port 443 is listening for HTTPS connections
   - Performs an HTTPS request to localhost and verifies:
     - Status code is 200
     - Response body contains "Hello, world!"
   - Checks SSL/TLS protocol security:
     - Verifies SSL3 protocol is disabled (security best practice)
     - Verifies TLS1.2 protocol is enabled
   - Resources: port (1), http (1), ssl (2)

## Dependencies

**External dependencies**: None specified in the files
**System package dependencies**: None explicitly required, but tests check for openssh-server
**Service dependencies**: Web server with HTTPS enabled on port 443

## Checks for the Migration

**Files to verify**:
- /etc/ssh/sshd_config (for SSH security test)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: localhost

**Tests to run**:
- SSH configuration validation
- HTTPS website availability and content validation
- SSL/TLS protocol security verification

## Pre-flight checks:
```bash
# SSH Security Test
# Check if SSH root login is disabled
grep -i "PermitRootLogin" /etc/ssh/sshd_config
# Or check if openssh-server is not installed
rpm -q openssh-server || echo "openssh-server is not installed"

# HTTPS Website Test
# Check if port 443 is listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Test HTTPS response
curl -k -s -o /dev/null -w "%{http_code}" https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# Check SSL/TLS protocols
nmap --script ssl-enum-ciphers -p 443 localhost | grep -E "SSLv3|TLSv1.2"
openssl s_client -ssl3 -connect localhost:443 </dev/null 2>&1 | grep "Protocol"
openssl s_client -tls1_2 -connect localhost:443 </dev/null 2>&1 | grep "Protocol"
```