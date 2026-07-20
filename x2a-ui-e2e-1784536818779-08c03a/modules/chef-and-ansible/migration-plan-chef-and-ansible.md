---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather an example of using Chef InSpec with Ansible. The module contains Ansible playbooks that set up an Apache web server with HTTPS support and SSL security fixes, along with InSpec tests for verification.

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
kitchen.yml
README.md
index.html
```

## Module Explanation

The module contains Ansible playbooks that perform operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs additional packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3)
   - Handlers: Restart apache, Restart sshd

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Modifies /etc/apache2/mods-available/ssl.conf to use only TLSv1.2
   - Resources: replace (1)
   - Handlers: Restart apache2, Restart sshd

3. **Test Verification**:
   - **tests/website_https_verify.rb**: InSpec tests to verify:
     - Port 443 is listening
     - HTTPS website returns 200 status and contains "Hello, world!"
     - SSL3 protocol is disabled
     - TLS1.2 protocol is enabled
   
   - **tests/ssh_profile.rb**: InSpec test to verify:
     - SSH root login is disabled for security compliance

## Dependencies

**External cookbook dependencies**: None (this is an Ansible playbook with InSpec tests)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution rather than being stored in the repository.

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
- Apache virtual host configuration (inline template) → /etc/apache2/sites-available/helloworld.conf (1 time)
- HTML content (inline template) → /var/www/helloworld/index.html (1 time)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
systemctl status sshd

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL certificate verification
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"
openssl verify -CAfile /etc/apache2/certs/apache.crt /etc/apache2/certs/apache.crt

# SSL protocol check
openssl s_client -connect localhost:443 -ssl3 </dev/null 2>/dev/null  # Should fail
openssl s_client -connect localhost:443 -tls1_2 </dev/null 2>/dev/null  # Should succeed

# Website availability
curl -k https://localhost/  # Should return 200 and contain "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP/1.1 200 OK

# Apache virtual host configuration
grep -r "SSLEngine on" /etc/apache2/sites-available/
grep -r "DocumentRoot" /etc/apache2/sites-available/

# SSL configuration check
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# File permissions
ls -la /etc/apache2/certs/
ls -la /var/www/helloworld/

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```