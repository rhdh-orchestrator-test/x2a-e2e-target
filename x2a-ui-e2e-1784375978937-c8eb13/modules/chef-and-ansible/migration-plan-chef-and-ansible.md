---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible playbooks. The module contains Ansible playbooks that set up an Apache web server with HTTPS support and SSL security configurations, along with InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: A single Apache web server instance
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
README.md
```

## Module Explanation

The module is actually a set of Ansible playbooks with Chef InSpec tests, not a traditional Chef cookbook. The operations are performed in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures a virtual host for HTTPS
   - Creates web content directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables the default Apache site
   - Enables the new virtual host
   - Activates SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to mitigate POODLE vulnerability
   - Modifies /etc/apache2/mods-available/ssl.conf to disable older SSL protocols
   - Sets SSLProtocol to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**:
     - Verifies port 443 is listening
     - Checks HTTPS response returns status 200
     - Confirms page content contains "Hello, world!"
     - Validates SSL3 protocol is disabled
     - Validates TLS1.2 protocol is enabled

   - **tests/ssh_profile.rb**:
     - Implements a security control to verify SSH root login is disabled
     - Checks /etc/ssh/sshd_config for PermitRootLogin setting
     - Provides compliance metadata (STIG IDs, CCI references)

## Dependencies

**External cookbook dependencies**: None (this is not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive.

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
- Apache virtual host configuration (rendered once)
- HTML content (rendered once)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl configtest
apache2ctl -M | grep ssl  # Should show ssl_module

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
openssl s_client -connect localhost:443 -tls1_2  # Should connect
openssl s_client -connect localhost:443 -ssl3    # Should fail

# Virtual host configuration
ls -la /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/helloworld.conf
cat /etc/apache2/sites-available/helloworld.conf

# Certificate verification
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"

# Web content
ls -la /var/www/helloworld/
cat /var/www/helloworld/index.html

# Web server functionality
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP/1.1 200 OK

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# SSH configuration (for compliance)
cat /etc/ssh/sshd_config | grep PermitRootLogin
```