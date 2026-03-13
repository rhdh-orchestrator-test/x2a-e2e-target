# Migration Plan: Chef InSpec Tests

**TLDR**: This module contains Chef InSpec tests for SSH security configuration and HTTPS website verification. It includes two test files: one that verifies SSH root login is disabled and another that checks HTTPS website functionality, including port listening, response status, content verification, and SSL/TLS protocol security.

## Service Type and Instances

**Service Type**: Testing Framework (InSpec)

**Configured Instances**:
- **SSH Security Test**: Tests that SSH root login is disabled
  - Location/Path: /etc/ssh/sshd_config
  - Key Config: PermitRootLogin parameter should not be 'yes'
  
- **HTTPS Website Test**: Tests HTTPS website functionality
  - Port/Socket: 443
  - Key Config: Verifies port listening, HTTP status 200, content matching, and TLS security

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

The Chef InSpec test module performs the following tests:

1. **SSH Security Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Tests that SSH root login is disabled for security compliance
   - Checks either:
     - The SSH configuration file has PermitRootLogin not set to 'yes'
     - OR the openssh-server package is not installed
   - Includes security metadata:
     - Security group: 'SRG-OS-000112'
     - Vulnerability ID: 'V-38607'
     - Rule ID: 'SV-50408r1_rule'
     - Severity: 'CAT I'
     - STIG ID: 'RHEL-08-000227'
     - CCI: 'CCI-000774'
   - Resources: sshd_config (1), package (1)

2. **HTTPS Website Test** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Tests that port 443 is listening
   - Verifies HTTPS website returns status code 200
   - Checks that response body contains "Hello, world!"
   - Ensures SSL3 protocol is disabled (security check)
   - Ensures TLS 1.2 protocol is enabled (security check)
   - Resources: port (1), http (1), ssl (2)

## Dependencies

**External cookbook dependencies**: None specified
**System package dependencies**: None specified (tests check for openssh-server)
**Service dependencies**: Web server with HTTPS enabled

## Checks for the Migration

**Files to verify**:
- /etc/ssh/sshd_config (for SSH test)

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: localhost

**Templates rendered**: None

## Pre-flight checks:
```bash
# SSH Security Test:
# Check SSH configuration
grep PermitRootLogin /etc/ssh/sshd_config
# Should NOT show "PermitRootLogin yes"

# Alternative check - if SSH server is not installed
rpm -q openssh-server || echo "openssh-server not installed"

# Verify SSH service if installed
if rpm -q openssh-server &>/dev/null; then
  systemctl status sshd
  # Check actual SSH login attempt (should fail)
  ssh -v root@localhost
  # Should show "Permission denied"
fi

# HTTPS Website Test:
# Check if port 443 is listening
netstat -tulpn | grep :443
ss -tlnp | grep :443

# Test HTTPS response
curl -k -I https://localhost/
# Should return HTTP/1.1 200 OK

# Test page content
curl -k https://localhost/ | grep "Hello, world!"
# Should find the text "Hello, world!"

# Test SSL/TLS protocols (requires nmap)
nmap --script ssl-enum-ciphers -p 443 localhost
# Should NOT show SSLv3
# Should show TLSv1.2

# Alternative SSL protocol check using openssl
echo | openssl s_client -connect localhost:443 -ssl3 2>&1 | grep "Protocol"
# Should indicate SSLv3 is not supported

echo | openssl s_client -connect localhost:443 -tls1_2 2>&1 | grep "Protocol"
# Should show "Protocol  : TLSv1.2"
```