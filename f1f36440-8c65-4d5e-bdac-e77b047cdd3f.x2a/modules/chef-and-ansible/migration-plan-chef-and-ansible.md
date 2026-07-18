---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but rather a set of Ansible playbooks with Chef InSpec tests. The repository contains Ansible playbooks for configuring an Apache web server with HTTPS and SSL security fixes, along with InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:

- **Apache HTTPS Server**: 
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

This is not a Chef cookbook but rather a set of Ansible playbooks with Chef InSpec tests. The repository demonstrates how to use Chef InSpec for compliance testing alongside Ansible for configuration management.

The repository contains:

1. **website_https.yml** (Ansible playbook):
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs curl, openssl, and python3-openssl
   - Creates SSL certificates directory at /etc/apache2/certs
   - Generates self-signed SSL certificates
   - Configures Apache virtual host for HTTPS
   - Deploys a simple "Hello World" website
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible playbook):
   - Fixes SSL configuration in Apache to mitigate POODLE vulnerability
   - Disables SSLv3 and enables only TLSv1.2
   - Resources: replace, service

3. **tests/website_https_verify.rb** (InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS website returns 200 status and contains "Hello, world!"
   - Ensures SSLv3 is disabled
   - Ensures TLSv1.2 is enabled

4. **tests/ssh_profile.rb** (InSpec test):
   - Verifies SSH root login is disabled for security compliance
   - Contains STIG compliance information

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-existing secrets.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline in playbook)
- HTML content (inline in playbook)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
openssl rsa -in /etc/apache2/certs/apache.key -check

# SSL protocol verification
openssl s_client -connect localhost:443 -ssl3  # Should fail
openssl s_client -connect localhost:443 -tls1_2  # Should succeed

# Website accessibility
curl -k https://localhost/  # Should return HTTP 200 with "Hello, world!"
curl -I -k https://localhost/  # Should show HTTP/1.1 200 OK

# Virtual host configuration
grep -r "SSLEngine on" /etc/apache2/sites-available/
grep -r "DocumentRoot" /etc/apache2/sites-available/

# SSL configuration check
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# SSH security check
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should not be "yes"

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache2
lsof -i :443

# Log verification
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```