---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module deploys an Apache web server with HTTPS enabled using a self-signed certificate, and includes InSpec tests for compliance verification.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS**: A single Apache web server instance
  - Location/Path: /var/www/helloworld
  - Port/Socket: 443 (HTTPS)
  - Key Config: SSL enabled with self-signed certificate, TLSv1.2 protocol

## File Structure

```
website_https.yml
poodle_fix.yml
tests/website_https_verify.rb
tests/ssh_profile.rb
index.html
kitchen.yml
```

## Module Explanation

The module is already an Ansible implementation with Chef InSpec tests for compliance verification. There is no Chef cookbook to migrate.

1. **website_https.yml**:
   - Installs Apache 2.4.41 web server package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates self-signed SSL certificate using OpenSSL
   - Configures Apache virtual host for HTTPS
   - Deploys a simple "Hello World" HTML page
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 protocol
   - Restarts Apache and SSH services
   - Resources: replace, service

3. **tests/website_https_verify.rb**:
   - InSpec test to verify HTTPS is working on port 443
   - Checks that the website returns a 200 status code
   - Verifies the content contains "Hello, world!"
   - Ensures SSL3 protocol is disabled
   - Ensures TLS1.2 protocol is enabled

4. **tests/ssh_profile.rb**:
   - InSpec test to verify SSH root login is disabled
   - Implements security compliance check for SSH configuration
   - Tagged with security identifiers (SRG-OS-000112, V-38607, etc.)

## Dependencies

**External cookbook dependencies**: None (this is an Ansible playbook, not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
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

# Web server connectivity
curl -k https://localhost/
curl -k -I https://localhost/

# SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail
nmap --script ssl-enum-ciphers -p 443 localhost

# Configuration validation
apache2ctl -t
apache2ctl -M | grep ssl
cat /etc/apache2/sites-available/helloworld.conf
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol

# Certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# File permissions
ls -la /etc/apache2/certs/
ls -la /var/www/helloworld/

# InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Special Note

This module is not actually a Chef cookbook that needs migration to Ansible. It is already an Ansible playbook with Chef InSpec tests for compliance verification. The module demonstrates how Chef InSpec can be used alongside Ansible for compliance testing.

The migration task is not applicable in this case, as the implementation is already in Ansible. The Chef components (InSpec tests) are being used for their intended purpose of compliance verification and would typically remain as InSpec tests even in an Ansible environment.