---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing with Ansible playbooks. The module contains Ansible playbooks that set up an Apache web server with HTTPS and SSL security configurations, along with InSpec tests to verify compliance.

## Service Type and Instances

**Service Type**: Web Server (Apache)

**Configured Instances**:
- **Apache HTTPS Server**: 
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
index.html
README.md
```

## Module Explanation

The module is not a Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing with Ansible. The Ansible playbooks perform the following operations:

1. **website_https.yml**:
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates at /etc/apache2/certs
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory at /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host and enables the new one
   - Enables SSL module in Apache
   - Resources: apt (2), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to mitigate POODLE vulnerability
   - Disables SSLv3 and enables only TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace (1), service (2)

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**: Verifies that:
     - Port 443 is listening
     - HTTPS website returns 200 status and contains "Hello, world!"
     - SSLv3 is disabled
     - TLSv1.2 is enabled
   - **tests/ssh_profile.rb**: Verifies that:
     - SSH root login is disabled for security compliance
     - Includes STIG references and compliance metadata

## Dependencies

**External cookbook dependencies**: None (this is not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected across files

No credentials or secrets were detected in this module. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-existing secrets.

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
- Ports listening: 443 (HTTPS)
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
openssl rsa -in /etc/apache2/certs/apache.key -check

# SSL protocol verification
openssl s_client -connect localhost:443 -ssl3 || echo "SSLv3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2 | grep "Protocol"  # Should show TLSv1.2

# Website accessibility
curl -k https://localhost/ | grep "Hello, world!"
curl -I -k https://localhost/  # Should return HTTP/1.1 200 OK

# Virtual host configuration
grep -r "VirtualHost" /etc/apache2/sites-enabled/
cat /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/ | grep helloworld

# SSL configuration for POODLE mitigation
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf  # Should show "SSLProtocol -all +TLSv1.2"

# SSH security configuration
grep "PermitRootLogin" /etc/ssh/sshd_config  # Should NOT be set to "yes"

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
```