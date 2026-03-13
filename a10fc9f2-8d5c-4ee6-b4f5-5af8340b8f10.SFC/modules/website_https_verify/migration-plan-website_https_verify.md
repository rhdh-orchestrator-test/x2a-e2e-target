# Migration Plan: website_https_verify

**TLDR**: This is a Chef InSpec test module that verifies HTTPS functionality on a web server. It checks port 443 is listening, the HTTPS site returns a 200 status with expected content, and validates SSL/TLS protocol security settings.

## Service Type and Instances

**Service Type**: Web Server Test Suite

**Configured Instances**:
- **localhost**: HTTPS web server test
  - Port: 443
  - Protocol: HTTPS
  - Expected Content: "Hello, world!"
  - Security Requirements: TLS 1.2 enabled, SSL3 disabled

## File Structure

```
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

The module performs tests in this order:

1. **Port Verification** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies that port 443 (HTTPS) is listening
   - Resources: port test (1)

2. **HTTPS Content Verification** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Makes an HTTPS request to localhost with SSL verification disabled
   - Verifies HTTP status code is 200
   - Verifies response body contains "Hello, world!"
   - Resources: http test (1)

3. **SSL Protocol Security Verification** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies that insecure SSL3 protocol is disabled on port 443
   - Verifies that secure TLS 1.2 protocol is enabled on port 443
   - Resources: ssl test (2)

## Dependencies

**External cookbook dependencies**: None identified
**System package dependencies**: None directly in the test file (but the tested system would need a web server with SSL/TLS support)
**Service dependencies**: Web server with HTTPS enabled

## Checks for the Migration

**Files to verify**:
- N/A (This is a test module, not a configuration module)

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: localhost

**Templates rendered**:
- N/A (This is a test module, not a configuration module)

## Pre-flight checks:
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

# Web server configuration
apache2ctl -t  # For Apache
nginx -t       # For Nginx

# Logs
tail -f /var/log/apache2/error.log  # For Apache
tail -f /var/log/nginx/error.log    # For Nginx
```