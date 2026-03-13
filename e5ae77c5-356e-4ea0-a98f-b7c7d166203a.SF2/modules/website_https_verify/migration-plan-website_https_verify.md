# Migration Plan: website_https_verify

**TLDR**: This is a test module that verifies HTTPS functionality on a web server. It checks port 443 is listening, HTTPS returns a 200 status with expected content, and validates SSL/TLS protocol security (disabling SSL3, enabling TLS1.2).

## Service Type and Instances

**Service Type**: Web Server (Apache with HTTPS)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled, TLS 1.2 enabled, SSL3 disabled

## File Structure

```
chef-and-ansible/tests/website_https_verify.rb
```

## Module Explanation

The module performs verification tests in this order:

1. **Port verification** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies that port 443 (HTTPS) is listening
   - Resources: port test (1)

2. **HTTPS content verification** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Makes an HTTPS request to localhost with SSL verification disabled
   - Verifies HTTP status code is 200
   - Verifies response body contains "Hello, world!"
   - Resources: http test (1)

3. **SSL protocol security verification** (`chef-and-ansible/tests/website_https_verify.rb`):
   - Verifies that SSL3 protocol is disabled on port 443
   - Verifies that TLS1.2 protocol is enabled on port 443
   - Resources: ssl test (2)

## Dependencies

**External cookbook dependencies**: None (this is a test file)
**System package dependencies**: Apache2, OpenSSL, curl
**Service dependencies**: apache2 service

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/sites-enabled/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- None (this is a test file)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache

# Port verification
netstat -tulpn | grep :443
ss -tlnp | grep :443
lsof -i :443

# HTTPS content verification
curl -k https://localhost/
curl -k -I https://localhost/

# SSL/TLS protocol verification
nmap --script ssl-enum-ciphers -p 443 localhost
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2

# Apache configuration verification
apache2ctl -t
apache2ctl -M | grep ssl
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# File verification
ls -la /var/www/helloworld/
cat /var/www/helloworld/index.html | grep "Hello, world!"
ls -la /etc/apache2/sites-enabled/ | grep helloworld
cat /etc/apache2/sites-available/helloworld.conf | grep -E "VirtualHost|SSLEngine|SSLCertificate"

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```