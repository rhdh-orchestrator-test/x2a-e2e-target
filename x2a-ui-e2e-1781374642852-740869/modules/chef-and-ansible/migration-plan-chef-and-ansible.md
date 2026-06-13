---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Chef cookbook but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible playbooks. The repository contains Ansible playbooks that set up an Apache web server with HTTPS and SSL security configurations, along with InSpec tests to verify compliance.

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
kitchen.yml
index.html
```

## Module Explanation

The repository demonstrates using Ansible for configuration management with Chef InSpec for compliance testing:

1. **website_https.yml**:
   - Installs Apache 2.4.41-4ubuntu3.10 package
   - Installs supporting packages: curl, openssl, python3-openssl
   - Creates directory for SSL certificates: /etc/apache2/certs
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web content directory: /var/www/helloworld
   - Deploys a simple "Hello World" HTML page
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Resources: apt (3), file (2), openssl_privatekey (1), openssl_csr (1), openssl_certificate (1), copy (2), command (3), service (2)

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to mitigate POODLE vulnerability
   - Modifies /etc/apache2/mods-available/ssl.conf to disable SSLv3 and only allow TLSv1.2
   - Restarts Apache and SSH services after changes
   - Resources: replace (1), service (2)

3. **InSpec Tests**:
   - **tests/website_https_verify.rb**:
     - Verifies port 443 is listening
     - Checks HTTPS response returns 200 status code
     - Confirms "Hello, world!" text appears in the response
     - Validates SSLv3 is disabled
     - Validates TLSv1.2 is enabled

   - **tests/ssh_profile.rb**:
     - Compliance test for SSH root login security
     - Verifies PermitRootLogin is not set to 'yes' in SSH configuration
     - Tagged with security requirements (SRG-OS-000112, V-38607, etc.)

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

No credentials or secrets were detected in this repository. All configuration values appear to be non-sensitive. The SSL certificates are generated during playbook execution and are not pre-existing secrets.

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
- Ports listening: 443
- Network interfaces: All interfaces (*)

**Templates rendered**:
- Apache virtual host configuration (inline template) → /etc/apache2/sites-available/helloworld.conf (1 instance)
- HTML content (inline template) → /var/www/helloworld/index.html (1 instance)

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
nmap --script ssl-enum-ciphers -p 443 localhost
# Should show TLSv1.2 enabled and SSLv3 disabled

# Web server functionality
curl -k https://localhost/
curl -k -s https://localhost/ | grep "Hello, world!"  # Should return the hello world text

# Configuration files
cat /etc/apache2/sites-available/helloworld.conf
cat /etc/apache2/mods-available/ssl.conf | grep "SSLProtocol"  # Should show "SSLProtocol -all +TLSv1.2"

# Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log

# Network listening
netstat -tulpn | grep 443
ss -tlnp | grep apache2
lsof -i :443

# Virtual host configuration
ls -la /etc/apache2/sites-enabled/  # Should show helloworld.conf and NOT 000-default.conf
```