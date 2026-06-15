---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a Chef cookbook but rather an Ansible playbook with Chef InSpec tests. The module deploys an Apache web server with HTTPS enabled using a self-signed certificate, and includes InSpec tests for compliance verification.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLSv1.2 protocol

## File Structure

```
No Chef recipes found
No Chef providers found
No Chef templates found
No Chef attributes found
```

## Module Explanation

This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module consists of:

1. **website_https.yml** (Ansible playbook):
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate for HTTPS
   - Configures Apache virtual host for HTTPS on port 443
   - Deploys a simple "Hello World" website to /var/www/helloworld
   - Enables SSL module in Apache
   - Disables default site and enables the new virtual host
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible playbook):
   - Secures Apache SSL configuration by disabling vulnerable protocols
   - Sets SSLProtocol to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

3. **tests/website_https_verify.rb** (Chef InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS response returns 200 status code
   - Confirms page content contains "Hello, world!"
   - Validates SSL3 protocol is disabled
   - Validates TLSv1.2 protocol is enabled

4. **tests/ssh_profile.rb** (Chef InSpec test):
   - Verifies SSH root login is disabled for security compliance
   - Checks either sshd_config has PermitRootLogin not set to 'yes' or openssh-server is not installed

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during deployment and are not pre-existing secrets.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/sites-enabled/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443 (HTTPS)
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline template in website_https.yml)
- HTML content (inline template in website_https.yml)

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

# SSL protocol verification
openssl s_client -connect localhost:443 -tls1_2 </dev/null | grep "Protocol"  # Should show TLSv1.2
openssl s_client -connect localhost:443 -ssl3 </dev/null 2>&1 | grep "Protocol"  # Should fail

# Website accessibility
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP/1.1 200 OK

# Virtual host configuration
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf symlink

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep "SSLProtocol"  # Should show "SSLProtocol -all +TLSv1.2"

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

# SSH security (related to the InSpec test)
grep "PermitRootLogin" /etc/ssh/sshd_config
```