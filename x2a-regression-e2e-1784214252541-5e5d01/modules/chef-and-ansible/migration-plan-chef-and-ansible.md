---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not actually a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module deploys an Apache web server with HTTPS enabled using a self-signed certificate. It includes InSpec tests for compliance verification.

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
index.html
kitchen.yml
README.md
```

## Module Explanation

This is not a Chef cookbook but an Ansible playbook with Chef InSpec tests. The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache 2.4.41-4ubuntu3.10
   - Installs additional packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web root directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default virtual host
   - Enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt, file, openssl_privatekey, openssl_csr, openssl_certificate, copy, command, service

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Replaces SSLProtocol configuration to only allow TLSv1.2
   - Restarts Apache and SSH services
   - Resources: replace, service

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**:
     - Verifies port 443 is listening
     - Checks HTTPS response returns 200 status code
     - Confirms page content contains "Hello, world!"
     - Ensures SSLv3 is disabled
     - Ensures TLSv1.2 is enabled
   
   - **tests/ssh_profile.rb**:
     - Checks SSH root login is disabled
     - Implements compliance controls with STIG references

## Dependencies

**External cookbook dependencies**: None (not a Chef cookbook)
**System package dependencies**: apache2, curl, openssl, python3-openssl
**Service dependencies**: apache2, sshd

## Credentials

**Detection Summary**: No credentials detected

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
- Apache virtual host configuration (inline in playbook)
- HTML content (inline in playbook)

## Pre-flight checks:
```bash
# Service status
systemctl status apache2
ps aux | grep apache2

# Apache configuration validation
apache2ctl -t
apache2ctl -M | grep ssl

# SSL configuration
cat /etc/apache2/mods-available/ssl.conf | grep SSLProtocol
openssl s_client -connect localhost:443 -tls1_2 </dev/null
openssl s_client -connect localhost:443 -ssl3 </dev/null  # Should fail

# Website accessibility
curl -k https://localhost/
curl -k https://localhost/ | grep "Hello, world!"

# Virtual host configuration
ls -la /etc/apache2/sites-available/helloworld.conf
ls -la /etc/apache2/sites-enabled/helloworld.conf
cat /etc/apache2/sites-available/helloworld.conf

# SSL certificates
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout | grep "Subject:"

# Network listening
netstat -tulpn | grep :443
ss -tlnp | grep apache

# Logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# SSH configuration (related to InSpec test)
cat /etc/ssh/sshd_config | grep PermitRootLogin
```