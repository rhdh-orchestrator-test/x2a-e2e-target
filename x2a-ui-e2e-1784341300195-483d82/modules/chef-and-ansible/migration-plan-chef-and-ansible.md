---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but an Ansible playbook with Chef InSpec tests. It deploys an Apache web server with HTTPS enabled using a self-signed certificate, and includes security hardening for SSL/TLS protocols. No migration is needed as it's already in Ansible format.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLSv1.2 only

## File Structure

```
website_https.yml
poodle_fix.yml
tests/website_https_verify.rb
tests/ssh_profile.rb
kitchen.yml
README.md
index.html
```

## Module Explanation

The module is already in Ansible format and performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs additional packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey, openssl_csr, openssl_certificate, copy (2), command (3)
   - Handlers: Restart apache, Restart sshd

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Sets SSLProtocol to "-all +TLSv1.2" to only allow TLSv1.2
   - Resources: replace (1)
   - Handlers: Restart apache2, Restart sshd

3. **Tests**:
   - **tests/website_https_verify.rb**: InSpec tests to verify:
     - Port 443 is listening
     - HTTPS site returns 200 status and contains "Hello, world!"
     - SSL3 protocol is disabled
     - TLS 1.2 protocol is enabled
   - **tests/ssh_profile.rb**: InSpec test to verify SSH root login is disabled

## Dependencies

**External cookbook dependencies**: None (this is an Ansible playbook, not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment rather than being stored in the repository.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/sites-enabled/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline template) → /etc/apache2/sites-available/helloworld.conf (1 time)
- HTML content (inline template) → /var/www/helloworld/index.html (1 time)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module enabled

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL protocol check
openssl s_client -connect localhost:443 -ssl3 </dev/null 2>/dev/null  # Should fail
openssl s_client -connect localhost:443 -tls1_2 </dev/null 2>/dev/null  # Should succeed

# Website accessibility
curl -k https://localhost/
curl -k -I https://localhost/  # Should return HTTP 200

# Content verification
curl -k https://localhost/ | grep "Hello, world!"

# Configuration files
cat /etc/apache2/sites-available/helloworld.conf
cat /etc/apache2/mods-available/ssl.conf | grep "SSLProtocol"  # Should show "-all +TLSv1.2"

# Virtual host configuration
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf and not 000-default.conf

# File permissions
ls -la /etc/apache2/certs/
ls -la /var/www/helloworld/

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443
lsof -i :443

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log
```