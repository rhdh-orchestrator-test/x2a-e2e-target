---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but an Ansible playbook with Chef InSpec tests. It deploys an Apache web server with HTTPS enabled using a self-signed certificate, configures a "Hello World" website, and includes security hardening for SSL/TLS protocols. The module includes InSpec tests to verify the deployment and security compliance.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **Apache2**: Web server with HTTPS enabled
  - Location/Path: /etc/apache2
  - Port/Socket: 443
  - Key Config: SSL/TLS enabled, TLSv1.2 only, self-signed certificate

## File Structure

```
No Chef recipes found
No Chef providers found
No Chef templates found
No Chef attributes found
```

## Module Explanation

This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module performs operations in this order:

1. **website_https.yml** (`chef-and-ansible/website_https.yml`):
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates self-signed SSL certificate:
     - Private key: /etc/apache2/certs/apache.key
     - CSR: /etc/apache2/certs/apache.csr
     - Certificate: /etc/apache2/certs/apache.crt
   - Configures Apache virtual host for HTTPS:
     - Creates config: /etc/apache2/sites-available/helloworld.conf
     - Sets DocumentRoot to /var/www/helloworld
     - Enables SSL with certificate paths
   - Creates website directory: /var/www/helloworld
   - Deploys HTML content to /var/www/helloworld/index.html
   - Disables default site: a2dissite 000-default
   - Enables new site: a2ensite helloworld
   - Enables SSL module: a2enmod ssl
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml** (`chef-and-ansible/poodle_fix.yml`):
   - Hardens SSL configuration to prevent POODLE vulnerability
   - Modifies /etc/apache2/mods-available/ssl.conf to disable SSLv3 and only allow TLSv1.2
   - Restarts Apache and SSH services after changes
   - Resources: replace (1), service (2)

3. **Tests** (`chef-and-ansible/tests/`):
   - **website_https_verify.rb**: InSpec tests to verify:
     - Port 443 is listening
     - HTTPS website returns 200 status code
     - Website content contains "Hello, world!"
     - SSLv3 is disabled
     - TLSv1.2 is enabled
   - **ssh_profile.rb**: InSpec test to verify SSH root login is disabled

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/apache2/sites-available/helloworld.conf
- /etc/apache2/mods-available/ssl.conf
- /var/www/helloworld/index.html
- /etc/apache2/certs/apache.key
- /etc/apache2/certs/apache.csr
- /etc/apache2/certs/apache.crt

**Service endpoints to check**:
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline template in website_https.yml)
- HTML content (inline template in website_https.yml)

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
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL protocol verification
openssl s_client -connect localhost:443 -tls1_2
# Should connect successfully

openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" or similar

# Website accessibility
curl -k https://localhost/
# Should return HTML with "Hello, world!"

curl -I -k https://localhost/
# Should return HTTP/1.1 200 OK

# Virtual host configuration
grep -r "SSLEngine on" /etc/apache2/sites-available/
grep -r "DocumentRoot" /etc/apache2/sites-available/

# SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Should show: SSLProtocol -all +TLSv1.2

# File permissions
ls -la /etc/apache2/certs/
ls -la /var/www/helloworld/

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep :443
lsof -i :443

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
journalctl -u apache2 -f
```