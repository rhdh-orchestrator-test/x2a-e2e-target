---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module deploys an Apache web server with HTTPS enabled using a self-signed certificate, and includes InSpec tests for compliance verification.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **Apache HTTPS Server**: A single Apache web server instance with HTTPS enabled
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443
  - Key Config: Uses self-signed SSL certificate, TLSv1.2 protocol

## File Structure

```
None - This is not a Chef cookbook but an Ansible playbook with InSpec tests
```

## Module Explanation

This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module consists of:

1. **website_https.yml** (Ansible playbook):
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates SSL certificate directory at /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS on port 443
   - Deploys a simple "Hello World" website to /var/www/helloworld
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml** (Ansible playbook):
   - Addresses SSL POODLE vulnerability by restricting protocols to TLSv1.2 only
   - Modifies /etc/apache2/mods-available/ssl.conf to disable older protocols
   - Resources: replace, service

3. **tests/website_https_verify.rb** (Chef InSpec test):
   - Verifies port 443 is listening
   - Checks HTTPS response returns 200 status code
   - Confirms "Hello, world!" text appears in response body
   - Validates SSL3 protocol is disabled
   - Validates TLSv1.2 protocol is enabled

4. **tests/ssh_profile.rb** (Chef InSpec test):
   - Verifies SSH root login is disabled for security compliance
   - Checks /etc/ssh/sshd_config for PermitRootLogin setting
   - Includes STIG compliance information (SRG-OS-000112, V-38607)

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
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.crt
- /etc/apache2/certs/apache.csr
- /etc/apache2/mods-available/ssl.conf

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- None (uses Ansible variables for inline templates)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Web server connectivity
curl -k https://localhost/
curl -k -I https://localhost/

# SSL configuration
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 || echo "SSL3 disabled (good)"

# Configuration validation
apache2ctl -t
apache2ctl -M | grep ssl
cat /etc/apache2/sites-available/helloworld.conf
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
ls -la /etc/apache2/sites-enabled/

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
ls -la /etc/apache2/certs/

# Content verification
cat /var/www/helloworld/index.html | grep "Hello, world!"

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log
journalctl -u apache2 -f

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache
lsof -i :443

# InSpec tests (if available)
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```